export type AllowedEventFilter = 'all' | 'failed';

const SCRIPT_TAG_REGEX = /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi;
const GENERIC_TAG_REGEX = /<\/?[^>]+>/gi;
const EVENT_HANDLER_REGEX = /on\w+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/gi;
const JAVASCRIPT_URI_REGEX = /javascript:/gi;

const EMAIL_REGEX =
  /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+$/;

const SQL_PATTERNS: RegExp[] = [
  /(\b(SELECT|UPDATE|DELETE|INSERT|DROP|UNION|ALTER)\b)/i,
  /('|--|;|\/\*|\*\/)/,
  /\bOR\b\s+['"]?\d+['"]?\s*=\s*['"]?\d+['"]?/i,
];

const DEFAULT_ALLOWED_MIME_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'application/pdf',
] as const;

const DEFAULT_ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.pdf'];

const ALLOWED_EVENT_FILTERS: AllowedEventFilter[] = ['all', 'failed'];

export interface FileValidationOptions {
  allowedMimeTypes?: readonly string[];
  allowedExtensions?: readonly string[];
  maxBytes?: number;
}

export const sanitizeHtmlInput = (value: string): string => {
  if (!value) return '';
  return value
    .replace(SCRIPT_TAG_REGEX, '')
    .replace(EVENT_HANDLER_REGEX, '')
    .replace(JAVASCRIPT_URI_REGEX, '')
    .replace(GENERIC_TAG_REGEX, '')
    .trim();
};

export const isValidEmail = (value: string): boolean => {
  if (!value) return false;
  return EMAIL_REGEX.test(value) && value.length <= 254;
};

export const detectSqlInjection = (value: string): boolean => {
  if (!value) return false;
  return SQL_PATTERNS.some((pattern) => pattern.test(value));
};

export const validateFileUpload = (
  file: { name: string; type: string; size: number },
  {
    allowedMimeTypes = DEFAULT_ALLOWED_MIME_TYPES,
    allowedExtensions = DEFAULT_ALLOWED_EXTENSIONS,
    maxBytes = 5 * 1024 * 1024,
  }: FileValidationOptions = {},
): boolean => {
  const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
  return (
    allowedMimeTypes.includes(file.type) &&
    allowedExtensions.includes(extension) &&
    file.size > 0 &&
    file.size <= maxBytes
  );
};

export const normalizeEventFilter = (value?: string | null): AllowedEventFilter => {
  if (!value) return 'all';
  const normalized = value.toLowerCase().trim();
  return ALLOWED_EVENT_FILTERS.includes(normalized as AllowedEventFilter) ? (normalized as AllowedEventFilter) : 'all';
};

export const redactSensitiveLogData = <T extends Record<string, unknown>>(data: T): T => {
  const clone = { ...data };
  Object.keys(clone).forEach((key) => {
    if (key.toLowerCase().includes('token') || key.toLowerCase().includes('password') || key.toLowerCase().includes('apikey')) {
      clone[key] = '***';
    }
  });
  return clone;
};

export class MemoryRateLimiter {
  private calls: Map<string, { count: number; resetTime: number }> = new Map();

  constructor(private readonly limit = 100, private readonly windowMs = 60_000) {}

  public canExecute(key: string): boolean {
    const now = Date.now();
    const existing = this.calls.get(key) ?? { count: 0, resetTime: now + this.windowMs };

    if (now > existing.resetTime) {
      existing.count = 0;
      existing.resetTime = now + this.windowMs;
    }

    if (existing.count >= this.limit) {
      this.calls.set(key, existing);
      return false;
    }

    existing.count += 1;
    this.calls.set(key, existing);
    return true;
  }
}
