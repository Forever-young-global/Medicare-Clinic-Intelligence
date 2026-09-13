import type {Metadata} from "next";import "./globals.css";
export const metadata:Metadata={title:"Roshsoft Intelligent Clinic",description:"Secure end-to-end clinic management by Roshsoft Technologies.",other:{"codex-preview":"development"},icons:{icon:"/favicon.svg",shortcut:"/favicon.svg"}};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
