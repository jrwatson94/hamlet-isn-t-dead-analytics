import path from "node:path";
import { CONFIG } from "./config";
import { log } from "./logger";
import { fetchAllMediaWithInsights, fetchIgAccountInfo } from "./graph";
import { normalizeApiRow, normalizeStoryCsvRow, unionHeaders } from "./normalize";
import { readCsv, writeCsv } from "./csv";
import { NormalizedRow } from "./types";

async function main() {
  log.info("Reading IG account info…");
  const acct = await fetchIgAccountInfo();
  const username = acct.username ?? "";
  const accountName = acct.name ?? "";

  log.info("Fetching ALL media with insights (auto-pagination) …");
  const media = await fetchAllMediaWithInsights();
  log.info(`Fetched ${media.length} media items.`);

  const apiRows: NormalizedRow[] = media.map((m) => normalizeApiRow(m, username, accountName));

  log.info(`Reading stories CSV: ${CONFIG.STORIES_CSV}`);
  const storiesCsv = await readCsv(path.resolve(process.cwd(), CONFIG.STORIES_CSV));
  const storyRows: NormalizedRow[] = storiesCsv.map(normalizeStoryCsvRow);

  const merged = [...apiRows, ...storyRows];
  const headers = unionHeaders(merged);

  log.info(`Writing merged CSV → ${CONFIG.OUTFILE}`);
  await writeCsv(path.resolve(process.cwd(), CONFIG.OUTFILE), merged, headers);

  log.info(`Done. Wrote ${merged.length} rows.`);
}

main().catch((err) => {
  log.error(err);
  process.exit(1);
});
