import { describe, it, expect } from 'vitest';
import {
    sanitizeHtmlInput,
    isValidEmail,
    detectSqlInjection,
    validateFileUpload,
    normalizeEventFilter,
    redactSensitiveLogData,
    MemoryRateLimiter,
} from '../../utils/security';

describe('Security Utils', () => {
    describe('sanitizeHtmlInput', () => {
        it('removes script tags', () => {
            const input = '<script>alert("xss")</script>Hello';
            const result = sanitizeHtmlInput(input);

            expect(result).not.toContain('<script>');
            expect(result).toBe('Hello');
        });

        it('removes event handlers', () => {
            const input = '<div onclick="malicious()">Text</div>';
            const result = sanitizeHtmlInput(input);

            expect(result).not.toContain('onclick');
            expect(result).toBe('Text');
        });

        it('removes javascript: URIs', () => {
            const input = '<a href="javascript:alert(1)">Link</a>';
            const result = sanitizeHtmlInput(input);

            expect(result).not.toContain('javascript:');
        });

        it('removes all HTML tags', () => {
            const input = '<p><strong>Bold</strong> text</p>';
            const result = sanitizeHtmlInput(input);

            expect(result).toBe('Bold text');
        });

        it('handles empty input', () => {
            expect(sanitizeHtmlInput('')).toBe('');
            expect(sanitizeHtmlInput(null as any)).toBe('');
        });
    });

    describe('isValidEmail', () => {
        it('validates correct emails', () => {
            expect(isValidEmail('user@example.com')).toBe(true);
            expect(isValidEmail('test.user@domain.co.uk')).toBe(true);
        });

        it('rejects invalid emails', () => {
            expect(isValidEmail('notanemail')).toBe(false);
            expect(isValidEmail('missing@domain')).toBe(false);
            expect(isValidEmail('@nodomain.com')).toBe(false);
            expect(isValidEmail('')).toBe(false);
        });

        it('rejects too long emails', () => {
            const longEmail = 'a'.repeat(250) + '@test.com';
            expect(isValidEmail(longEmail)).toBe(false);
        });
    });

    describe('detectSqlInjection', () => {
        it('detects SQL keywords', () => {
            expect(detectSqlInjection('SELECT * FROM users')).toBe(true);
            expect(detectSqlInjection('DROP TABLE data')).toBe(true);
            expect(detectSqlInjection('UNION SELECT password')).toBe(true);
        });

        it('detects SQL characters', () => {
            expect(detectSqlInjection("' OR '1'='1")).toBe(true);
            expect(detectSqlInjection('--comment')).toBe(true);
            expect(detectSqlInjection('/* comment */')).toBe(true);
        });

        it('allows safe input', () => {
            expect(detectSqlInjection('normal text')).toBe(false);
            expect(detectSqlInjection('user@email.com')).toBe(false);
        });

        it('handles empty input', () => {
            expect(detectSqlInjection('')).toBe(false);
        });
    });

    describe('validateFileUpload', () => {
        it('accepts valid files', () => {
            const file = {
                name: 'document.pdf',
                type: 'application/pdf',
                size: 1024 * 1024, // 1MB
            };

            expect(validateFileUpload(file)).toBe(true);
        });

        it('rejects invalid MIME type', () => {
            const file = {
                name: 'script.exe',
                type: 'application/x-msdownload',
                size: 1024,
            };

            expect(validateFileUpload(file)).toBe(false);
        });

        it('rejects invalid extension', () => {
            const file = {
                name: 'file.exe',
                type: 'image/jpeg', // Lying about type
                size: 1024,
            };

            expect(validateFileUpload(file)).toBe(false);
        });

        it('rejects files exceeding max size', () => {
            const file = {
                name: 'large.jpg',
                type: 'image/jpeg',
                size: 10 * 1024 * 1024, // 10MB (default max is 5MB)
            };

            expect(validateFileUpload(file)).toBe(false);
        });

        it('rejects zero-size files', () => {
            const file = {
                name: 'empty.jpg',
                type: 'image/jpeg',
                size: 0,
            };

            expect(validateFileUpload(file)).toBe(false);
        });

        it('accepts custom options', () => {
            const file = {
                name: 'custom.txt',
                type: 'text/plain',
                size: 100,
            };

            const result = validateFileUpload(file, {
                allowedMimeTypes: ['text/plain'],
                allowedExtensions: ['.txt'],
                maxBytes: 1000,
            });

            expect(result).toBe(true);
        });
    });

    describe('normalizeEventFilter', () => {
        it('normalizes valid filters', () => {
            expect(normalizeEventFilter('ALL')).toBe('all');
            expect(normalizeEventFilter('failed')).toBe('failed');
            expect(normalizeEventFilter('  FAILED  ')).toBe('failed');
        });

        it('defaults to "all" for invalid input', () => {
            expect(normalizeEventFilter('invalid')).toBe('all');
            expect(normalizeEventFilter(null)).toBe('all');
            expect(normalizeEventFilter(undefined)).toBe('all');
            expect(normalizeEventFilter('')).toBe('all');
        });
    });

    describe('redactSensitiveLogData', () => {
        it('redacts tokens', () => {
            const data = { authToken: 'secret123', other: 'value' };
            const result = redactSensitiveLogData(data);

            expect(result.authToken).toBe('***');
            expect(result.other).toBe('value');
        });

        it('redacts passwords', () => {
            const data = { username: 'admin', password: 'secret' };
            const result = redactSensitiveLogData(data);

            expect(result.password).toBe('***');
            expect(result.username).toBe('admin');
        });

        it('redacts API keys', () => {
            const data = { apikey: '12345', data: 'public' };
            const result = redactSensitiveLogData(data);

            expect(result.apikey).toBe('***');
        });

        it('does not modify original object', () => {
            const data = { token: 'original' };
            const result = redactSensitiveLogData(data);

            expect(data.token).toBe('original');
            expect(result.token).toBe('***');
        });
    });

    describe('MemoryRateLimiter', () => {
        it('allows execution within limit', () => {
            const limiter = new MemoryRateLimiter(5, 1000);

            expect(limiter.canExecute('user1')).toBe(true);
            expect(limiter.canExecute('user1')).toBe(true);
            expect(limiter.canExecute('user1')).toBe(true);
        });

        it('blocks execution when limit exceeded', () => {
            const limiter = new MemoryRateLimiter(3, 10000);

            limiter.canExecute('user1');
            limiter.canExecute('user1');
            limiter.canExecute('user1');

            expect(limiter.canExecute('user1')).toBe(false);
        });

        it('tracks different keys independently', () => {
            const limiter = new MemoryRateLimiter(2, 10000);

            limiter.canExecute('user1');
            limiter.canExecute('user1');

            // user1 is at limit, but user2 is not
            expect(limiter.canExecute('user1')).toBe(false);
            expect(limiter.canExecute('user2')).toBe(true);
        });
    });
});
