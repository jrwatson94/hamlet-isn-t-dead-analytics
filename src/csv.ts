import fs from "node:fs/promises";
import path from "node:path";
import { parse } from "csv-parse/sync";
import { stringify } from "csv-stringify/sync";
import { CsvRow, NormalizedRow } from "./types";
import { log } from "./logger";
import { DateTime } from "luxon";

function toUtcIsoFromNY(raw: string): string {
  if (!raw || !raw.trim()) return "";

  // Try multiple possible formats:
  const formats = [
    "M/d/yy H:mm",         // e.g. 5/29/25 5:04
    "M/d/yyyy H:mm",       // e.g. 5/29/2025 5:04
    "M/d/yy h:mm a",       // e.g. 5/29/25 5:04 PM
    "M/d/yyyy h:mm a",
    "yyyy-MM-dd'T'HH:mm:ssZZ", // ISO-like
  ];

  for (const fmt of formats) {
    const dt = DateTime.fromFormat(raw, fmt, { zone: "America/New_York" });
    if (dt.isValid) return dt.toUTC().toISO();
  }

  // Try ISO parse as fallback
  const iso = DateTime.fromISO(raw, { zone: "America/New_York" });
  if (iso.isValid) return iso.toUTC().toISO();

  return ""; // unparseable
}

export async function readCsv(filePath: string): Promise<CsvRow[]> {
  let buf = await fs.readFile(filePath);
  if (buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf) {
    buf = buf.slice(3);
  }

  const rows = parse(buf, { columns: true, skip_empty_lines: true }) as CsvRow[];

  // → Normalize publish time column here
  for (const r of rows) {
    if ("Publish time" in r && r["Publish time"]) {
      r["Publish time"] = toUtcIsoFromNY(r["Publish time"]);
    }
  }

  log.info(`Loaded ${rows.length} rows from ${path.basename(filePath)}`);
  return rows;
}

export async function writeCsv(filePath: string, rows: NormalizedRow[], headers: string[]) {
  const csv = stringify(rows, { header: true, columns: headers });
  await fs.writeFile(filePath, csv);
}
