"""Conservative structure-aware byte spans for FreeCol XML.

This module locates exact byte ranges; it does not authorize deletions or
replace the independent survivor verifier required in Phase 2D-0 M2.
"""
import re
from xml.parsers import expat


class UnsafeXMLSpan(ValueError):
    pass


def _start_tag_end(data, start):
    """Return (end-exclusive, empty) with quote-aware > detection."""
    quote = None
    i = start
    while i < len(data):
        c = data[i]
        if quote is not None:
            if c == quote:
                quote = None
        elif c in (34, 39):
            quote = c
        elif c == 62:
            j = i - 1
            while j > start and data[j] in (9, 10, 13, 32):
                j -= 1
            return i + 1, data[j] == 47
        i += 1
    raise UnsafeXMLSpan('Unterminated XML start tag')


def element_spans(data):
    """Return (path, tag, attributes, start, end) for every XML element.

    Paths are sibling ordinals from root, independent of duplicate IDs.
    Exact original bytes are retained, never reserialized.
    """
    if not isinstance(data, bytes):
        raise UnsafeXMLSpan('Expected XML bytes')
    if re.search(br'<!\s*(DOCTYPE|ENTITY)\b', data, re.I):
        raise UnsafeXMLSpan('DOCTYPE/entity declaration unsupported')
    if re.search(br'<\?xml\s+[^?]*encoding\s*=\s*["\x27](?!utf-8["\x27])', data[:256], re.I):
        raise UnsafeXMLSpan('Only UTF-8 supported')
    if data.startswith((b'\xff\xfe', b'\xfe\xff')) or b'\x00' in data:
        raise UnsafeXMLSpan('Only UTF-8 supported')
    parser = expat.ParserCreate()
    stack = []
    children = []
    result = []

    def start(tag, attrs):
        if ':' in tag or ':' in attrs or any(':' in k for k in attrs):
            raise UnsafeXMLSpan('Namespace-prefixed XML unsupported')
        begin = parser.CurrentByteIndex
        if data[begin:begin + 1] != b'<':
            raise UnsafeXMLSpan('Start offset mismatch')
        ending, empty = _start_tag_end(data, begin)
        index = children[-1] if children else 0
        if children:
            children[-1] += 1
        path = stack[-1][0] + (index,) if stack else ()
        stack.append((path, tag, dict(attrs), begin, ending, empty))
        children.append(0)

    def end(tag):
        if not stack:
            raise UnsafeXMLSpan('Unbalanced XML')
        path, name, attrs, begin, start_end, empty = stack.pop()
        children.pop()
        at = parser.CurrentByteIndex
        if name != tag:
            raise UnsafeXMLSpan('Tag mismatch')
        if empty:
            if at != start_end:
                raise UnsafeXMLSpan('Empty tag offset mismatch')
            ending = start_end
        else:
            closing = b'</' + name.encode('utf-8')
            if data[at:at + len(closing)] != closing:
                raise UnsafeXMLSpan('Closing tag offset mismatch')
            ending, is_empty = _start_tag_end(data, at)
            if is_empty:
                raise UnsafeXMLSpan('Malformed closing tag')
        result.append((path, name, attrs, begin, ending))

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    try:
        parser.Parse(data, True)
    except (expat.ExpatError, UnicodeError) as exc:
        raise UnsafeXMLSpan(str(exc)) from exc
    return sorted(result, key=lambda item: item[3])


def spans_for_id(data, tag, identifier):
    matches = [(start, end) for _, name, attrs, start, end in element_spans(data)
               if name == tag and attrs.get('id') == identifier]
    if not matches:
        raise UnsafeXMLSpan('Missing ' + tag + ' definition for ' + identifier)
    return matches
