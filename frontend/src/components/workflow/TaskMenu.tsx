import { Registry } from "@/components/airflow-tasks/RegistryCohortsTest";

const groupTasksByType = () => {
  const grouped = Object.values(Registry).reduce((acc, task) => {
    const type = task.type || "Unknown";
    const subtype = task.subtype || null;
    const taskName = Object.keys(Registry).find((k) => Registry[k] === task);
    if (!taskName) return acc;

    acc[type] ??= {};
    acc[type][subtype ?? "_no_subtype"] ??= [];
    acc[type][subtype ?? "_no_subtype"].push(taskName);
    return acc;
  }, {} as Record<string, Record<string, string[]>>);

  return Object.entries(grouped).map(([type, subtypes]) => ({
    name: type,
    subtypes: Object.entries(subtypes).map(([name, items]) => ({
      name: name === "_no_subtype" ? null : name,
      items,
    })),
  }));
};

interface TaskMenuProps {
  onAddComponent: (item: string) => void;
}

export function TaskMenu({ onAddComponent }: TaskMenuProps) {
  const categories = groupTasksByType();

  return (
    <ul className="menu menu-bordered bg-base-200 rounded-box w-full text-md">
      {categories.map((category) => (
        <li key={category.name}>
          <details>
            <summary>{category.name}</summary>
            <ul>
              {category.subtypes.map((sub) =>
                sub.name ? (
                  <li key={sub.name}>
                    <details>
                      <summary>{sub.name}</summary>
                      <ul>
                        {sub.items.map((item) => (
                          <li key={item}>
                            <a onClick={() => onAddComponent(item)}>{item}</a>
                          </li>
                        ))}
                      </ul>
                    </details>
                  </li>
                ) : (
                  sub.items.map((item) => (
                    <li key={item}>
                      <a onClick={() => onAddComponent(item)}>{item}</a>
                    </li>
                  ))
                )
              )}
            </ul>
          </details>
        </li>
      ))}
    </ul>
  );
}
