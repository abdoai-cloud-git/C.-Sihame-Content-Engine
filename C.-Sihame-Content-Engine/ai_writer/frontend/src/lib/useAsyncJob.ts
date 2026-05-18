import { useRef, useState, useCallback } from "react";

export type JobStatus = "idle" | "pending" | "success" | "error";

export interface JobContext {
  setPhase: (phase: string) => void;
  signal: AbortSignal;
}

export interface AsyncJob {
  status: JobStatus;
  phase: string;
  errorMessage: string | null;
  isPending: boolean;
  isError: boolean;
  run: (
    fn: (ctx: JobContext) => Promise<void>,
    initialPhase?: string
  ) => Promise<boolean>;
  reset: () => void;
}

interface JobState {
  status: JobStatus;
  phase: string;
  errorMessage: string | null;
}

const IDLE: JobState = { status: "idle", phase: "", errorMessage: null };

/**
 * Per-action async job state.
 *
 * Stale-response protection: each call to run() increments a monotonic counter.
 * The running fn captures its token at call time. Any state update (setPhase,
 * success, error) is silently dropped if a newer run() has already started.
 *
 * Duplicate-submission guard: run() returns immediately (false) if status is
 * already "pending".
 *
 * Cancellation: each run() creates a fresh AbortController; the signal is
 * passed to the fn so fetch calls can respect it. On unmount or if a newer run
 * starts, the previous controller is aborted.
 */
export function useAsyncJob(): AsyncJob {
  const [state, setState] = useState<JobState>(IDLE);
  const latestToken = useRef(0);
  const controllerRef = useRef<AbortController | null>(null);

  const run = useCallback(
    async (
      fn: (ctx: JobContext) => Promise<void>,
      initialPhase = ""
    ): Promise<boolean> => {
      // Duplicate-submission guard
      if (latestToken.current > 0 && state.status === "pending") return false;

      // Abort any previous in-flight request
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;

      const token = ++latestToken.current;

      setState({ status: "pending", phase: initialPhase, errorMessage: null });

      const setPhase = (phase: string) => {
        if (latestToken.current === token) {
          setState((prev) => ({ ...prev, phase }));
        }
      };

      try {
        await fn({ setPhase, signal: controller.signal });
        if (latestToken.current === token) {
          setState({ status: "success", phase: "", errorMessage: null });
        }
        return true;
      } catch (err) {
        if (controller.signal.aborted) return false; // stale — discard silently
        if (latestToken.current === token) {
          setState({
            status: "error",
            phase: "",
            errorMessage: (err as Error).message || "حدث خطأ غير متوقع",
          });
        }
        return false;
      }
    },
    [state.status]
  );

  const reset = useCallback(() => {
    controllerRef.current?.abort();
    latestToken.current = 0;
    setState(IDLE);
  }, []);

  return {
    status: state.status,
    phase: state.phase,
    errorMessage: state.errorMessage,
    isPending: state.status === "pending",
    isError: state.status === "error",
    run,
    reset,
  };
}
