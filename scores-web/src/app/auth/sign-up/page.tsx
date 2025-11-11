export default function SignUpPage() {
  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-4 px-4 py-20 text-center">
      <h1 className="text-3xl font-semibold tracking-tight">
        Create Organiser Account
      </h1>
      <p className="text-sm text-muted-foreground">
        Self-service registration will launch alongside the FastAPI backend.
        Until then, drop us a line and we&apos;ll help you onboard your event.
      </p>
    </div>
  );
}

