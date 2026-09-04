import AppKit
import ApplicationServices
import CoreGraphics
import Foundation

private enum DisplayManagerError: LocalizedError {
    case message(String)

    var errorDescription: String? {
        switch self {
        case .message(let text): return text
        }
    }
}

private struct Display {
    let id: CGDirectDisplayID
    let name: String
    let frame: CGRect
    let visibleFrame: CGRect
    let isPrimary: Bool

    var pixels: String {
        "\(CGDisplayPixelsWide(id)) × \(CGDisplayPixelsHigh(id))"
    }
}

private func accessibilityFrame(for appKitFrame: CGRect, in desktop: CGRect) -> CGRect {
    CGRect(
        x: appKitFrame.origin.x,
        y: desktop.maxY - appKitFrame.maxY,
        width: appKitFrame.width,
        height: appKitFrame.height
    )
}

private func displays() throws -> [Display] {
    let screens = NSScreen.screens
    guard !screens.isEmpty else {
        throw DisplayManagerError.message("No active displays were found.")
    }

    let desktop = screens.reduce(CGRect.null) { $0.union($1.frame) }
    let primaryID = CGMainDisplayID()
    let result = try screens.map { screen -> Display in
        guard let number = screen.deviceDescription[NSDeviceDescriptionKey("NSScreenNumber")] as? NSNumber else {
            throw DisplayManagerError.message("Could not identify a connected display.")
        }

        let id = CGDirectDisplayID(number.uint32Value)
        return Display(
            id: id,
            name: screen.localizedName,
            frame: accessibilityFrame(for: screen.frame, in: desktop),
            visibleFrame: accessibilityFrame(for: screen.visibleFrame, in: desktop),
            isPrimary: id == primaryID
        )
    }

    return result.sorted {
        if $0.isPrimary != $1.isPrimary { return $0.isPrimary }
        return $0.name.localizedStandardCompare($1.name) == .orderedAscending
    }
}

private func alfredItems(for activeDisplays: [Display]) throws {
    let duplicateNames = Dictionary(grouping: activeDisplays, by: \.name)
        .filter { $0.value.count > 1 }
        .map(\.key)

    var items: [[String: Any]] = activeDisplays.map { display in
        let role = display.isPrimary ? "Main Display" : "Secondary Display"
        let identifier = duplicateNames.contains(display.name) ? " · Display ID \(display.id)" : ""
        return [
            "uid": "display-\(display.id)",
            "title": display.isPrimary ? "★ \(display.name)" : display.name,
            "subtitle": "\(role) · \(display.pixels)\(identifier)",
            "arg": String(display.id),
            "valid": true
        ]
    }

    if activeDisplays.count > 1 {
        items.append(contentsOf: [
            [
                "uid": "display-next",
                "title": "Next Display",
                "subtitle": "Move the focused window to the next display",
                "arg": "next",
                "valid": true
            ],
            [
                "uid": "display-previous",
                "title": "Previous Display",
                "subtitle": "Move the focused window to the previous display",
                "arg": "previous",
                "valid": true
            ]
        ])
    }

    let output: [String: Any] = ["items": items]
    let data = try JSONSerialization.data(withJSONObject: output, options: [])
    print(String(decoding: data, as: UTF8.self))
}

private func focusedWindow() throws -> AXUIElement {
    guard AXIsProcessTrusted() else {
        throw DisplayManagerError.message(
            "Accessibility permission is required. Enable Alfred (and this workflow helper, if shown) in System Settings > Privacy & Security > Accessibility."
        )
    }

    let systemWide = AXUIElementCreateSystemWide()
    var appValue: CFTypeRef?
    guard AXUIElementCopyAttributeValue(systemWide, kAXFocusedApplicationAttribute as CFString, &appValue) == .success,
          let appValue,
          CFGetTypeID(appValue) == AXUIElementGetTypeID() else {
        throw DisplayManagerError.message("Could not find the focused application.")
    }

    let application = unsafeBitCast(appValue, to: AXUIElement.self)
    var windowValue: CFTypeRef?
    guard AXUIElementCopyAttributeValue(application, kAXFocusedWindowAttribute as CFString, &windowValue) == .success,
          let windowValue,
          CFGetTypeID(windowValue) == AXUIElementGetTypeID() else {
        throw DisplayManagerError.message("The focused application does not have a movable window.")
    }

    let window = unsafeBitCast(windowValue, to: AXUIElement.self)
    var minimized: CFTypeRef?
    if AXUIElementCopyAttributeValue(window, kAXMinimizedAttribute as CFString, &minimized) == .success,
       let minimized,
       CFGetTypeID(minimized) == CFBooleanGetTypeID(),
       CFBooleanGetValue(unsafeBitCast(minimized, to: CFBoolean.self)) {
        throw DisplayManagerError.message("The focused window is minimized. Restore it before moving it.")
    }

    var fullScreen: CFTypeRef?
    if AXUIElementCopyAttributeValue(window, "AXFullScreen" as CFString, &fullScreen) == .success,
       let fullScreen,
       CFGetTypeID(fullScreen) == CFBooleanGetTypeID(),
       CFBooleanGetValue(unsafeBitCast(fullScreen, to: CFBoolean.self)) {
        throw DisplayManagerError.message("Native macOS full-screen windows cannot be moved between displays.")
    }

    return window
}

private func rect(of window: AXUIElement) throws -> CGRect {
    var positionValue: CFTypeRef?
    var sizeValue: CFTypeRef?
    guard AXUIElementCopyAttributeValue(window, kAXPositionAttribute as CFString, &positionValue) == .success,
          AXUIElementCopyAttributeValue(window, kAXSizeAttribute as CFString, &sizeValue) == .success,
          let positionValue,
          let sizeValue,
          CFGetTypeID(positionValue) == AXValueGetTypeID(),
          CFGetTypeID(sizeValue) == AXValueGetTypeID() else {
        throw DisplayManagerError.message("The focused window does not expose its bounds.")
    }

    var position = CGPoint.zero
    var size = CGSize.zero
    guard AXValueGetValue(unsafeBitCast(positionValue, to: AXValue.self), .cgPoint, &position),
          AXValueGetValue(unsafeBitCast(sizeValue, to: AXValue.self), .cgSize, &size) else {
        throw DisplayManagerError.message("The focused window returned invalid bounds.")
    }
    return CGRect(origin: position, size: size)
}

private func target(named target: String, displays: [Display], windowFrame: CGRect) throws -> Display {
    if target == "primary" {
        guard let primary = displays.first(where: \.isPrimary) else {
            throw DisplayManagerError.message("Could not identify the main display.")
        }
        return primary
    }

    guard let sourceIndex = displays.indices.max(by: {
        intersectionArea(windowFrame, displays[$0].frame) < intersectionArea(windowFrame, displays[$1].frame)
    }) else {
        throw DisplayManagerError.message("Could not identify the source display.")
    }

    if target == "next" || target == "previous" {
        guard displays.count > 1 else {
            throw DisplayManagerError.message("Only one display is connected.")
        }
        let offset = target == "next" ? 1 : displays.count - 1
        return displays[(sourceIndex + offset) % displays.count]
    }

    guard let id = UInt32(target), let display = displays.first(where: { $0.id == id }) else {
        throw DisplayManagerError.message("The selected display is no longer connected. Try again.")
    }
    return display
}

private func intersectionArea(_ lhs: CGRect, _ rhs: CGRect) -> CGFloat {
    let intersection = lhs.intersection(rhs)
    return intersection.isNull ? 0 : intersection.width * intersection.height
}

private func clampedFrame(_ frame: CGRect, inside bounds: CGRect) -> CGRect {
    let width = min(frame.width, bounds.width)
    let height = min(frame.height, bounds.height)
    return CGRect(
        x: min(max(frame.origin.x, bounds.minX), bounds.maxX - width),
        y: min(max(frame.origin.y, bounds.minY), bounds.maxY - height),
        width: width,
        height: height
    )
}

private func move(window: AXUIElement, to destination: Display, among activeDisplays: [Display]) throws {
    let oldFrame = try rect(of: window)
    guard let source = activeDisplays.max(by: {
        intersectionArea(oldFrame, $0.frame) < intersectionArea(oldFrame, $1.frame)
    }) else {
        throw DisplayManagerError.message("Could not identify the source display.")
    }

    let sourceBounds = source.visibleFrame
    let destinationBounds = destination.visibleFrame
    guard sourceBounds.width > 0, sourceBounds.height > 0 else {
        throw DisplayManagerError.message("The source display has invalid bounds.")
    }

    let relativeX = (oldFrame.minX - sourceBounds.minX) / sourceBounds.width
    let relativeY = (oldFrame.minY - sourceBounds.minY) / sourceBounds.height
    let scaledFrame = CGRect(
        x: destinationBounds.minX + relativeX * destinationBounds.width,
        y: destinationBounds.minY + relativeY * destinationBounds.height,
        width: oldFrame.width * destinationBounds.width / sourceBounds.width,
        height: oldFrame.height * destinationBounds.height / sourceBounds.height
    )
    let newFrame = clampedFrame(scaledFrame, inside: destinationBounds)

    var position = newFrame.origin
    var size = newFrame.size
    guard let positionValue = AXValueCreate(.cgPoint, &position),
          let sizeValue = AXValueCreate(.cgSize, &size),
          AXUIElementSetAttributeValue(window, kAXSizeAttribute as CFString, sizeValue) == .success,
          AXUIElementSetAttributeValue(window, kAXPositionAttribute as CFString, positionValue) == .success else {
        throw DisplayManagerError.message("macOS did not allow the focused window to be moved. Check Accessibility permission and whether the app supports window management.")
    }
}

private func run() throws {
    let arguments = Array(CommandLine.arguments.dropFirst())
    guard let command = arguments.first else {
        throw DisplayManagerError.message("Usage: display-manager list | move <display-id|primary|next|previous>")
    }

    let activeDisplays = try displays()
    switch command {
    case "list":
        try alfredItems(for: activeDisplays)
    case "move":
        guard arguments.count == 2 else {
            throw DisplayManagerError.message("Choose a display before moving the focused window.")
        }
        let window = try focusedWindow()
        let windowFrame = try rect(of: window)
        let destination = try target(named: arguments[1], displays: activeDisplays, windowFrame: windowFrame)
        try move(window: window, to: destination, among: activeDisplays)
    default:
        throw DisplayManagerError.message("Unknown command: \(command)")
    }
}

do {
    try run()
} catch {
    fputs("Window Manager: \(error.localizedDescription)\n", stderr)
    exit(1)
}
