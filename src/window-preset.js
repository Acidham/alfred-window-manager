#!/usr/bin/osascript -l JavaScript
// Fit the frontmost window to a preset area of its screen's visible frame.
// Usage: window-preset.js <preset>
//
// Replaces Alfred's core "Resize Window from Preset" task, which (1) reserves a
// menu bar on secondary displays even when "Displays have separate Spaces" is
// off, and (2) sets position once, so a move that lands short leaves the window
// short and its size clipped at the screen edge.

ObjC.import("AppKit")

// Usable area (window coordinates), preset, current size -> target rectangle
function layout(a, preset, current) {
  switch (preset) {
    case "maximise":              return [a.x, a.y, a.w, a.h]
    case "half-left":             return [a.x, a.y, a.w / 2, a.h]
    case "half-right":            return [a.x + a.w / 2, a.y, a.w / 2, a.h]
    case "half-top":              return [a.x, a.y, a.w, a.h / 2]
    case "half-bottom":           return [a.x, a.y + a.h / 2, a.w, a.h / 2]
    case "third-left":            return [a.x, a.y, a.w / 3, a.h]
    case "third-centrewidth":     return [a.x + a.w / 3, a.y, a.w / 3, a.h]
    case "third-right":           return [a.x + a.w * 2 / 3, a.y, a.w / 3, a.h]
    case "twothirds-centrewidth": return [a.x + a.w / 6, a.y, a.w * 2 / 3, a.h]
    case "centre": {
      const w = Math.min(current[0], a.w)
      const h = Math.min(current[1], a.h)
      return [a.x + (a.w - w) / 2, a.y + (a.h - h) / 2, w, h]
    }
    default: throw "Unknown preset: " + preset
  }
}

// Window position and size -> usable area of the screen holding the window's centre
function usableArea(pos, size) {
  const screens = $.NSScreen.screens.js
  const primary = screens.find(s => s.frame.origin.x === 0 && s.frame.origin.y === 0)
  const primaryHeight = primary.frame.size.height

  // Window coordinates are top-left based, screen coordinates bottom-left based
  const midX = pos[0] + size[0] / 2
  const midY = primaryHeight - (pos[1] + size[1] / 2)
  const screen = screens.find(s => {
    const f = s.frame
    return midX >= f.origin.x && midX < f.origin.x + f.size.width &&
           midY >= f.origin.y && midY < f.origin.y + f.size.height
  }) || primary

  const v = screen.visibleFrame
  return {
    x: v.origin.x,
    y: primaryHeight - (v.origin.y + v.size.height),
    w: v.size.width,
    h: v.size.height
  }
}

function run(argv) {
  const process = Application("System Events").applicationProcesses.where({ frontmost: true })[0]
  const win = process.windows.where({ subrole: "AXStandardWindow" })[0]

  const pos = win.position()
  const size = win.size()
  const [x, y, w, h] = layout(usableArea(pos, size), argv[0], size).map(Math.round)

  // Repeat until it lands; stop early for apps that won't fit exactly
  // (e.g. a minimum width, or terminals that resize in character cells).
  let previous = ""
  for (let i = 0; i < 6; i++) {
    win.position = [x, y]
    delay(0.1)
    win.size = [w, h]
    delay(0.1)

    const p = win.position()
    const s = win.size()
    if (Math.abs(p[0] - x) <= 1 && Math.abs(p[1] - y) <= 1 &&
        Math.abs(s[0] - w) <= 1 && Math.abs(s[1] - h) <= 1) return

    const current = [p[0], p[1], s[0], s[1]].join(",")
    if (current === previous) return
    previous = current
  }
}
