export interface GraphError {
  error?: {
    message?: string;
    type?: string;
    code?: number;
    error_subcode?: number;
    fbtrace_id?: string;
  };
}

export interface GraphPaging {
  cursors?: { before?: string; after?: string };
  next?: string;
  previous?: string;
}

export interface InsightDatum {
  name: string;
  period?: string;
  values: Array<number | { value: number }>;
  title?: string;
  description?: string;
  id?: string;
}

export interface InsightsBlock {
  data: InsightDatum[];
}

export interface MediaItem {
  id: string;
  caption?: string;
  media_type?: string;
  media_url?: string;
  permalink?: string;
  thumbnail_url?: string;
  timestamp?: string;
  insights?: InsightsBlock;
}

export interface MediaResponse extends GraphError {
  data?: MediaItem[];
  paging?: GraphPaging;
}

export interface IgAccountInfo {
  id?: string;
  username?: string;
  name?: string;
}

export interface NormalizedRow {
  [key: string]: string | number | "";
}

export type CsvRow = Record<string, string>;
