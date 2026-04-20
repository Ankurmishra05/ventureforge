import Link from "next/link";

type ErrorStateProps = {
  message: string;
  onRetry: () => void;
  requiresAuth?: boolean;
};

export function ErrorState({ message, onRetry, requiresAuth = false }: ErrorStateProps) {
  return (
    <div className="rounded-[1.75rem] border border-rose-400/20 bg-rose-400/10 p-8">
      <p className="text-sm font-medium uppercase tracking-[0.28em] text-rose-200">
        Request failed
      </p>
      <h3 className="mt-4 font-display text-2xl font-semibold text-white">
        The startup brief could not be generated
      </h3>
      <p className="mt-3 max-w-2xl text-sm leading-7 text-rose-100/85">{message}</p>
      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={onRetry}
          className="inline-flex items-center justify-center rounded-full border border-white/15 bg-white/10 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-white/15"
        >
          Try again
        </button>
        {requiresAuth ? (
          <Link
            href="/login"
            className="inline-flex items-center justify-center rounded-full border border-white/15 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-white/10"
          >
            Go to login
          </Link>
        ) : null}
      </div>
    </div>
  );
}
