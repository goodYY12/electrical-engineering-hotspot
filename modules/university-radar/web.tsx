import type { SVGProps } from "react";
import { defineWebModule } from "@aihot/web/modules";

function RadarIcon({ size = 18, ...props }: SVGProps<SVGSVGElement> & { size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.7} aria-hidden="true" {...props}><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5" /><path d="M12 3v18M3 12h18M12 12l6-5" /></svg>;
}

export const UNIVERSITY_RADAR_WEB = defineWebModule({
  name: "university-radar",
  sidebar: { section: "内容", items: [{ to: "/university-radar", label: "高校科研雷达", icon: RadarIcon }] },
  tools: [{ to: "/university-radar", label: "高校科研雷达", icon: <RadarIcon size={18} /> }, { to: "/graduation-topics", label: "毕业设计选题", icon: <RadarIcon size={18} /> }],
});
