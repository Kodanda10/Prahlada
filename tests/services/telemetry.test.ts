import { describe, it, expect, vi, beforeEach } from 'vitest';
import { telemetryService } from '../../services/telemetry';
import { apiService } from '../../services/api';

vi.mock('../../services/api', () => ({
    apiService: {
        post: vi.fn(),
    },
}));

describe('Telemetry Service', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Mock console methods
        vi.spyOn(console, 'error').mockImplementation(() => { });
        vi.spyOn(console, 'warn').mockImplementation(() => { });
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    describe('logError', () => {
        it('logs error to backend', async () => {
            const error = new Error('Test error');
            const errorInfo = { componentStack: 'Component stack trace' };

            await telemetryService.logError(error, errorInfo);

            expect(apiService.post).toHaveBeenCalledWith(
                '/api/telemetry',
                expect.objectContaining({
                    type: 'error',
                    name: 'Error',
                    data: expect.objectContaining({
                        message: 'Test error',
                        stack: expect.any(String),
                        componentStack: 'Component stack trace',
                    }),
                })
            );
        });

        it('handles backend failure gracefully', async () => {
            (apiService.post as any).mockRejectedValueOnce(new Error('Network error'));

            const error = new Error('Test error');

            await expect(telemetryService.logError(error)).resolves.not.toThrow();
            expect(console.warn).toHaveBeenCalled();
        });
    });

    describe('logAction', () => {
        it('logs user action to backend', async () => {
            const action = 'button_click';
            const details = { button: 'submit', page: 'login' };

            await telemetryService.logAction(action, details);

            expect(apiService.post).toHaveBeenCalledWith(
                '/api/telemetry',
                expect.objectContaining({
                    type: 'action',
                    name: 'button_click',
                    data: details,
                })
            );
        });

        it('logs action without details', async () => {
            await telemetryService.logAction('page_loaded');

            expect(apiService.post).toHaveBeenCalledWith(
                '/api/telemetry',
                expect.objectContaining({
                    type: 'action',
                    name: 'page_loaded',
                })
            );
        });
    });

    describe('logPerformance', () => {
        it('logs performance metric', async () => {
            await telemetryService.logPerformance('page_load_time', 1234);

            expect(apiService.post).toHaveBeenCalledWith(
                '/api/telemetry',
                expect.objectContaining({
                    type: 'performance',
                    name: 'page_load_time',
                    data: { value: 1234 },
                })
            );
        });
    });

    describe('logNavigation', () => {
        it('logs navigation event', async () => {
            await telemetryService.logNavigation('/dashboard');

            expect(apiService.post).toHaveBeenCalledWith(
                '/api/telemetry',
                expect.objectContaining({
                    type: 'navigation',
                    name: 'route_change',
                    data: { path: '/dashboard' },
                })
            );
        });
    });

    describe('Timestamp and URL', () => {
        it('includes timestamp in all events', async () => {
            const beforeTime = Date.now();

            await telemetryService.logAction('test');

            const call = (apiService.post as any).mock.calls[0][1];
            expect(call.timestamp).toBeGreaterThanOrEqual(beforeTime);
        });
    });
});
