import Link from "next/link";

export default function HomePage() {
  return (
    <main
      className="min-h-screen bg-contain bg-no-repeat bg-center flex items-center justify-center bg-opacity-10"
      style={{ backgroundImage: "url('/bg.jpg')" }}
    >
      <div className="text-center max-w-2xl ">
        <h1 className="text-5xl font-bold mb-4 text-gray-900">Welcome!</h1>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <a
            href="/dashboard"
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-6 rounded transition "
          >
            Dashboard
          </a>

          <a
            href="/workflow/editor"
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-6 rounded transition "
          >
            Create a workflow!
          </a>

          {/* <a
            href="/workflow/test"
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-6 rounded transition "
          >
            Test your workflow!
          </a> */}
        </div>
      </div>
    </main>
  );
}
