import { DM_Sans } from "next/font/google";

export const fontSans = DM_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-dm-sans",
  display: "swap",
});

export const fontVariables = `${fontSans.variable}`;
