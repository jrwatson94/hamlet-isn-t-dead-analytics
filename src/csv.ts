import fs from "node:fs/promises";
import path from "node:path";
import { parse } from "csv-parse/sync";
import { stringify } from "csv-stringify/sync";
import { CsvRow, NormalizedRow } from "./types";
import { log } from "./logger";

export async function readCsv(filePath: string): Promise<CsvRow[]> {
  const buf = await fs.readFile(filePath);
  const rows = parse(buf, { columns: true, skip_empty_lines: true }) as CsvRow[];
  log.info(`Loaded ${rows.length} rows from ${path.basename(filePath)}`);
  return rows;
}

export async function writeCsv(filePath: string, rows: NormalizedRow[], headers: string[]) {
  const csv = stringify(rows, { header: true, columns: headers });
  await fs.writeFile(filePath, csv);
}
