import { useState, useEffect } from 'react';

type ReviewStatusState = {
    showApproved: boolean;
    showPending: boolean;
    showSkipped: boolean;
};

type Listener = (state: ReviewStatusState) => void;

let state: ReviewStatusState = {
    showApproved: true,
    showPending: true,
    showSkipped: true,
};

const listeners = new Set<Listener>();

const notifyListeners = () => {
    listeners.forEach((listener) => listener({ ...state }));
};

export const reviewStatusStore = {
    getState: () => ({ ...state }),

    toggleApproved: () => {
        state.showApproved = !state.showApproved;
        notifyListeners();
    },

    togglePending: () => {
        state.showPending = !state.showPending;
        notifyListeners();
    },

    toggleSkipped: () => {
        state.showSkipped = !state.showSkipped;
        notifyListeners();
    },

    subscribe: (listener: Listener) => {
        listeners.add(listener);
        return () => listeners.delete(listener);
    }
};

export const useReviewStatus = () => {
    const [statusState, setStatusState] = useState<ReviewStatusState>(reviewStatusStore.getState());

    useEffect(() => {
        const unsubscribe = reviewStatusStore.subscribe(setStatusState);
        return () => { unsubscribe(); };
    }, []);

    return {
        ...statusState,
        toggleApproved: reviewStatusStore.toggleApproved,
        togglePending: reviewStatusStore.togglePending,
        toggleSkipped: reviewStatusStore.toggleSkipped,
    };
};
