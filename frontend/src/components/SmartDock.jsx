import { Palette, Music, Building, Book } from "lucide-react";

const items = [
  { id: "art", icon: Palette },
  { id: "music", icon: Music },
  { id: "architecture", icon: Building },
  { id: "story", icon: Book },
];

export default function SmartDock({ active, setActive }) {
  return (
    <div className="w-20 h-full flex flex-col items-center gap-4 pt-8 pb-4 bg-glass backdrop-blur-xl border-r border-purple-500/20 shrink-0">
      {items.map(({ id, icon: Icon }) => {
        const isActive = active === id;
        return (
          <button
            key={id}
            onClick={() => setActive(isActive ? null : id)}
            className={`p-3.5 rounded-xl transition-all duration-200 ${isActive
                ? "bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg shadow-purple-500/50 text-white scale-110"
                : "bg-white/5 text-white/60 hover:bg-white/10 hover:text-white hover:scale-105"
              }`}
          >
            <Icon strokeWidth={isActive ? 2.5 : 2} className="w-6 h-6" />
          </button>
        );
      })}
    </div>
  );
}