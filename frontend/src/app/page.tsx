import Link from 'next/link';
import Navbar from '@/components/Navbar';

export default function HomePage() {
  return (
    <main className="flex min-h-full flex-col items-center justify-center bg-gray-100 text-gray-900 p-6">
      <Navbar />
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome!</h1>
        <div className="flex justify-center gap-4 mt-6">
          <Link href="/editor" className="btn btn-lg btn-active btn-primary">
            Try the Workflow Editor
          </Link>
        </div>
      </div>
    </main>
  );
}
