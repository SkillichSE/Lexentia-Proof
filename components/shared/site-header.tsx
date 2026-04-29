import Link from "next/link";

const navItems = [
  { href: "/", label: "home" },
  { href: "/articles", label: "articles" },
  { href: "/author/dashboard", label: "author" }
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-zinc-800 bg-black/90 backdrop-blur">
      <div className="klyxe-container flex h-14 items-center justify-between">
        <Link href="/" className="font-semibold tracking-tight">
          klyxe <span className="klyxe-accent">lab</span>
        </Link>
        <nav className="flex items-center gap-4 text-sm text-zinc-300">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="hover:text-zinc-100">
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
