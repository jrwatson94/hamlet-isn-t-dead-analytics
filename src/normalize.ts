import { MediaItem, NormalizedRow } from "./types";
import { CONFIG } from "./config";

function firstValue(v: unknown): number | "" {
  if (Array.isArray(v) && v.length) {
    const val = v[0] as unknown;
    if (typeof val === "number") return val;
    if (typeof val === "object" && val !== null && "value" in (val as any)) {
      const num = (val as any).value;
      return typeof num === "number" ? num : "";
    }
  }
  return "";
}

function flattenInsights(item?: MediaItem): Record<string, number | ""> {
  const result: Record<string, number | ""> = {};
  const data = item?.insights?.data ?? [];
  for (const m of data) {
    if (!m?.name) continue;
    result[m.name] = firstValue(m.values);
  }
  return result;
}

/**
 * Normalize an API media item into the shared union column shape.
 * Story-specific fields are intentionally blank here.
 */
export function normalizeApiRow(
  item: MediaItem,
  username = "",
  accountName = ""
): NormalizedRow {
  const metrics = flattenInsights(item);
  return {
    "Source": "API",
    "Post ID": item.id || "",
    "Account ID": CONFIG.IG_USER_ID,
    "Account username": username,
    "Account name": accountName,
    "Description": item.caption || "",
    "Duration (sec)": "",
    "Publish time": item.timestamp || "",
    "Permalink": item.permalink || "",
    "Post type": item.media_type || "",
    "Data comment": "Lifetime",
    "Date": "Lifetime",
    // Story-ish columns (not applicable)
    "Views": metrics["plays"] ?? "",
    "Reach": metrics["reach"] ?? "",
    "Likes": metrics["likes"] ?? "",
    "Shares": metrics["shares"] ?? "",
    "Replies": "",
    "Navigation": "",
    "Profile visits": "",
    "Link clicks": "",
    "Sticker taps": "",
    // Extra API metrics
    "Impressions": metrics["impressions"] ?? "",
    "Comments": metrics["comments"] ?? "",
    "Saves": metrics["saves"] ?? "",
    "Total Interactions": metrics["total_interactions"] ?? "",
    "Media URL": item.media_url || "",
    "Thumbnail URL": item.thumbnail_url || ""
  };
}

/**
 * Normalize a STORIES CSV row (already expired stories) to the union shape.
 * Leave API-only fields blank.
 */
export function normalizeStoryCsvRow(row: Record<string, string>): NormalizedRow {
  return {
    "Source": "Stories CSV",
    "Post ID": row["Post ID"] ?? row["PostID"] ?? "",
    "Account ID": row["Account ID"] ?? "",
    "Account username": row["Account username"] ?? "",
    "Account name": row["Account name"] ?? "",
    "Description": row["Description"] ?? "",
    "Duration (sec)": row["Duration (sec)"] ?? "",
    "Publish time": row["Publish time"] ?? "",
    "Permalink": row["Permalink"] ?? "",
    "Post type": row["Post type"] ?? "",
    "Data comment": row["Data comment"] ?? "",
    "Date": row["Date"] ?? "",
    "Views": row["Views"] ?? "",
    "Reach": row["Reach"] ?? "",
    "Likes": row["Likes"] ?? "",
    "Shares": row["Shares"] ?? "",
    "Replies": row["Replies"] ?? "",
    "Navigation": row["Navigation"] ?? "",
    "Profile visits": row["Profile visits"] ?? "",
    "Link clicks": row["Link clicks"] ?? "",
    "Sticker taps": row["Sticker taps"] ?? "",
    // API-only fields left blank
    "Impressions": "",
    "Comments": "",
    "Saves": "",
    "Total Interactions": "",
    "Media URL": "",
    "Thumbnail URL": ""
  };
}

export const PREFERRED_ORDER = [
  "Source",
  "Post ID",
  "Account ID",
  "Account username",
  "Account name",
  "Description",
  "Duration (sec)",
  "Publish time",
  "Permalink",
  "Post type",
  "Data comment",
  "Date",
  "Views",
  "Reach",
  "Likes",
  "Shares",
  "Replies",
  "Navigation",
  "Profile visits",
  "Link clicks",
  "Sticker taps",
  "Impressions",
  "Comments",
  "Saves",
  "Total Interactions",
  "Media URL",
  "Thumbnail URL"
] as const;

export function unionHeaders(rows: NormalizedRow[]): string[] {
  const set = new Set<string>();
  for (const r of rows) {
    Object.keys(r).forEach((k) => set.add(k));
  }
  const ordered = PREFERRED_ORDER.filter((h) => set.has(h as string));
  const rest = [...set].filter((h) => !ordered.includes(h as any));
  return [...ordered, ...rest];
}
