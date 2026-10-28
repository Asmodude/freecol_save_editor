/*
 * Optional read-only FreeCol production bridge for OC-001.
 *
 * Compile against a matching FreeCol installation/development build:
 *   javac -cp "freecol.jar:lib/*" -d bridge-build tools/java/HammerProductionProbe.java
 *   java -cp "bridge-build:freecol.jar:lib/*" HammerProductionProbe save.fsg
 *
 * Windows: replace ':' classpath separators with ';'.
 * The caller MUST supply a copy of the save and a matching FreeCol build.
 * No save-writing operations are invoked.
 */
import java.io.File;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import net.sf.freecol.common.io.FreeColSavegameFile;
import net.sf.freecol.common.model.Colony;
import net.sf.freecol.common.model.GoodsType;
import net.sf.freecol.common.model.Player;
import net.sf.freecol.server.FreeColServer;
import net.sf.freecol.server.model.ServerGame;

public final class HammerProductionProbe {
    private HammerProductionProbe() {}

    private static String escape(String text) {
        return text.replace("\\", "\\\\").replace("\t", " ").replace("\n", " ");
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("Usage: HammerProductionProbe <save-copy.fsg>");
            System.exit(2);
        }
        try {
            // Uses the actual FreeCol server-side deserializer and production
            // engine. May reject saves from incompatible game versions.
            FreeColSavegameFile save = new FreeColSavegameFile(new File(args[0]));
            ServerGame game = FreeColServer.readGame(save, null, null);
            if (game == null || game.getSpecification() == null) {
                throw new IllegalStateException("FreeCol did not load a game/ruleset");
            }
            GoodsType hammers = game.getSpecification().getGoodsType("model.goods.hammers");
            if (hammers == null) {
                throw new IllegalStateException("No Hammers goods type in this ruleset");
            }
            List<String> rows = new ArrayList<>();
            game.getPlayers(player -> true).forEach(player -> {
                player.getColonies().forEach(colony -> {
                    // Total = gross work-location output; net = after consumers.
                    int gross = colony.getTotalProductionOf(hammers);
                    int net = colony.getNetProductionOf(hammers);
                    rows.add(escape(colony.getId()) + "\t"
                             + escape(player.getId()) + "\t" + gross + "\t" + net
                             + "\t" + escape(colony.getName())
                             + "\t" + escape(player.getNationId()));
                });
            });
            rows.sort(Comparator.naturalOrder());
            System.out.println("FREECOL_HAMMERS_V1\tcolony_id\towner_id\tgross\tnet\tcolony_name\tnation_id");
            for (String row : rows) System.out.println(row);
        } catch (Exception failure) {
            System.err.println("FreeCol production probe failed: " + failure);
            System.exit(3);
        }
    }
}
