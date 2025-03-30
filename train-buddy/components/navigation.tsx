"use client"

import { useState } from "react"
import Link from "next/link"
import { Menu, Home } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { cn } from "@/lib/utils"
import { usePathname } from "next/navigation"

export default function Navigation() {
  const [open, setOpen] = useState(false)
  const pathname = usePathname()

  const isHomePage = pathname === "/"
  const showBackButton = !isHomePage && pathname !== "/hub"

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        {showBackButton ? (
          <Button variant="ghost" size="icon" asChild className="mr-auto">
            <Link href={pathname.includes("/week1/day") ? "/week1" : pathname.includes("/week1") ? "/hub" : "/"}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="lucide lucide-chevron-left"
              >
                <path d="m15 18-6-6 6-6" />
              </svg>
              <span className="sr-only">Back</span>
            </Link>
          </Button>
        ) : (
          <div className="mr-auto"></div>
        )}

        <div className="flex items-center justify-center flex-1">
          {pathname === "/hub" && <h1 className="text-lg font-semibold">User Hub</h1>}
          {pathname === "/week1" && <h1 className="text-lg font-semibold">Week 1</h1>}
          {pathname.includes("/week1/day") && (
            <h1 className="text-lg font-semibold">{pathname.split("/").pop()?.replace("day", "Day ")}</h1>
          )}
          {pathname.includes("/exercise") && <h1 className="text-lg font-semibold">Exercise</h1>}
        </div>

        <div className="flex items-center justify-end space-x-2">
          {!isHomePage &&
            pathname !== "/loading" &&
            pathname !== "/loading2" &&
            pathname !== "/form" &&
            !pathname.includes("/exercise") && (
              <Button variant="ghost" size="icon" asChild>
                <Link href="/hub">
                  <Home className="h-5 w-5" />
                  <span className="sr-only">Home</span>
                </Link>
              </Button>
            )}

          {pathname.includes("/exercise") && (
            <Button variant="ghost" size="icon">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="lucide lucide-camera"
              >
                <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" />
                <circle cx="12" cy="13" r="3" />
              </svg>
              <span className="sr-only">Camera</span>
            </Button>
          )}

          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[240px] sm:w-[300px]">
              <nav className="flex flex-col gap-4 mt-8">
                <Link
                  href="/"
                  className={cn(
                    "flex items-center gap-2 text-lg font-semibold",
                    pathname === "/" ? "text-primary" : "text-muted-foreground",
                  )}
                  onClick={() => setOpen(false)}
                >
                  Home
                </Link>
                <Link
                  href="/about"
                  className={cn(
                    "flex items-center gap-2 text-lg font-semibold",
                    pathname === "/about" ? "text-primary" : "text-muted-foreground",
                  )}
                  onClick={() => setOpen(false)}
                >
                  About Us
                </Link>
                <Link
                  href="/contact"
                  className={cn(
                    "flex items-center gap-2 text-lg font-semibold",
                    pathname === "/contact" ? "text-primary" : "text-muted-foreground",
                  )}
                  onClick={() => setOpen(false)}
                >
                  Contact Us
                </Link>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}

