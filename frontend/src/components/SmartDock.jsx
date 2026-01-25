import { Palette, Music, Building, Book, MessageCircle } from "lucide-react";

const items = [
  { id: "art", icon: Palette },
  { id: "music", icon: Music },
  { id: "architecture", icon: Building },
  { id: "story", icon: Book },
  { id: "chat", icon: MessageCircle }
];

export default function SmartDock({ active, setActive }) {
  return (
    <div className="w-16 h-full flex flex-col items-center gap-8 py-8 bg-glass backdrop-blur-xl border-r border-white/10">
      {items.map(({ id, icon: Icon }) => (
        <button
          key={id}
          onClick={() => setActive(active === id ? null : id)}
          className={`p-3 rounded-xl transition ${
            active === id ? "bg-white/20" : "hover:bg-white/10"
          }`}
        >
          <Icon className="w-5 h-5 text-white/80" />
        </button>
      ))}
    </div>
  );
}