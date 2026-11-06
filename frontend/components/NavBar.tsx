import type { ComponentType, SVGProps } from "react";
import { ChatIcon, FolderIcon, LogoIcon, SettingsIcon } from "./Icons";
import styles from "./NavBar.module.css";

export type NavSection = "chat" | "documents" | "settings";

const items: {
  id: NavSection;
  label: string;
  icon: ComponentType<SVGProps<SVGSVGElement>>;
}[] = [
  { id: "chat", label: "Chat", icon: ChatIcon },
  { id: "documents", label: "Documents", icon: FolderIcon },
  { id: "settings", label: "Settings", icon: SettingsIcon },
];

interface NavBarProps {
  active: NavSection;
  onSelect: (section: NavSection) => void;
}

export default function NavBar({ active, onSelect }: NavBarProps) {
  return (
    <nav className={styles.nav} aria-label="Main">
      <div className={styles.brand}>
        <LogoIcon width={24} height={24} />
        <span className={styles.brandText}>foRAGe fairy</span>
      </div>
      <ul className={styles.list}>
        {items.map(({ id, label, icon: Icon }) => (
          <li key={id}>
            <button
              type="button"
              className={`${styles.item} ${active === id ? styles.active : ""}`}
              aria-current={active === id ? "page" : undefined}
              onClick={() => onSelect(id)}
              title={label}
            >
              <Icon />
              <span className={styles.label}>{label}</span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
