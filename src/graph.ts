import { CONFIG } from "./config";
import { GraphError, IgAccountInfo, MediaItem, MediaResponse } from "./types";
import { log } from "./logger";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function getJson<T>(url: string, attempt = 1): Promise<T> {
  const res = await fetch(url);
  if (res.ok) return (await res.json()) as T;

  let body: GraphError = {};
  try {
    body = (await res.json()) as GraphError;
  } catch {
    /* ignore */
  }

  const code = body?.error?.code;
  const subcode = body?.error?.error_subcode;
  const isRate =
    code === 4 || code === 17 || code === 613 || subcode === 2446079;

  if (isRate && attempt <= CONFIG.MAX_RETRIES) {
    const backoff = CONFIG.BACKOFF_BASE_MS * attempt * attempt;
    log.warn(`Rate limit; retrying in ${backoff}ms (attempt ${attempt})`);
    await sleep(backoff);
    return getJson<T>(url, attempt + 1);
  }

  log.error("Graph API error:", JSON.stringify(body));
  throw new Error(`Graph API request failed (HTTP ${res.status})`);
}

export async function fetchIgAccountInfo(): Promise<IgAccountInfo> {
  const u = new URL(
    `https://graph.facebook.com/${CONFIG.GRAPH_VERSION}/${CONFIG.IG_USER_ID}`
  );
  u.searchParams.set("fields", "username,name");
  u.searchParams.set("access_token", CONFIG.ACCESS_TOKEN);
  const data = await getJson<IgAccountInfo>(u.toString());
  return data;
}

export async function fetchAllMediaWithInsights(): Promise<MediaItem[]> {
  const fields = [
    "id",
    "caption",
    "media_type",
    "media_url",
    "permalink",
    "thumbnail_url",
    "timestamp",
    "insights.metric(impressions,reach,plays,views,likes,comments,saved,shares,follows,total_interactions)"
  ].join(",");

  let pageUrl = new URL(
    `https://graph.facebook.com/${CONFIG.GRAPH_VERSION}/${CONFIG.IG_USER_ID}/media`
  );
  pageUrl.searchParams.set("fields", fields);
  pageUrl.searchParams.set("limit", "100");
  pageUrl.searchParams.set("access_token", CONFIG.ACCESS_TOKEN);

  const out: MediaItem[] = [];

  // calculate cutoff once
  const cutoff = new Date();
  cutoff.setMonth(cutoff.getMonth() - 36); // ~2.5 years

  while (pageUrl) {
    const json = await getJson<MediaResponse>(pageUrl.toString());
    const batch = Array.isArray(json.data) ? json.data : [];
    out.push(...batch);

    // ===== STOP PAGINATION IF OLDEST ITEM IS BEYOND CUTOFF =====
    const last = batch[batch.length - 1];
    if (last?.timestamp) {
      const ts = new Date(last.timestamp);
      if (ts < cutoff) {
        console.log("[info] Reached media older than 3 years — stopping pagination.");
        break;
      }
    }

    const next = json?.paging?.next;
    if (!next) break;

    pageUrl = new URL(next);
    await sleep(150);
  }

  return out;
}

