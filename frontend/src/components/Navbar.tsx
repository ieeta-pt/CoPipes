import ThemeControllerButton from "@/components/ThemeControllerButton";

export default function Navbar() {
  return (
    <div className="navbar bg-base-100 shadow-sm">
      <a className="btn btn-ghost text-xl">daisyUI</a>
      <div>
        <ThemeControllerButton />
      </div>
    </div>
  );
}
