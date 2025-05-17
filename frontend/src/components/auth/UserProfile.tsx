import { useAuthStore } from "@/api/stores/authStore";

export default function UserProfile() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  if (!user) {
    return null;
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Profile</h2>

      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-500">Email</p>
          <p className="font-medium">{user.email}</p>
        </div>

        {user.full_name && (
          <div>
            <p className="text-sm text-gray-500">Full Name</p>
            <p className="font-medium">{user.full_name}</p>
          </div>
        )}

        <div>
          <p className="text-sm text-gray-500">Account Created</p>
          <p className="font-medium">
            {new Date(user.created_at).toLocaleDateString()}
          </p>
        </div>

        <div className="pt-4">
          <button
            onClick={() => logout()}
            className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
