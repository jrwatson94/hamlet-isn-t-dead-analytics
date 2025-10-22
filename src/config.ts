import dotenv from "dotenv";
dotenv.config();

function required(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`Missing required env var: ${name}`);
  return v;
}

export const CONFIG = {
  ACCESS_TOKEN: required("META_SYSTEM_USER_TOKEN"),
  IG_USER_ID: process.env.IG_USER_ID || "17841400539558029",
  GRAPH_VERSION: process.env.GRAPH_VERSION || "v21.0",
  STORIES_CSV: process.env.STORIES_CSV || "stories.csv",
  OUTFILE: process.env.OUTFILE || "merged.csv",
  BACKOFF_BASE_MS: 500,
  MAX_RETRIES: 5
} as const;
