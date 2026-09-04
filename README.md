# Alfred Window Manager
Alfred Workflow to move/resize/position windows.

**For actions like Left/Right Position, Maximize, and Center Two Thirds, the workflow saves the Window state so that you can restore it at any time.**

<img src="README.assets/win_manager.png" alt="win_manager" width=800 />

## Requirements

* [Automation Tasks](https://www.alfredapp.com/help/workflows/automations/automation-task/)
* macOS 12 or later
* Accessibility permission for Alfred in **System Settings → Privacy & Security → Accessibility**

## Usage

* Use keyword `wm` to invoke Window Manager
* Use `wms` to select a currently connected display by name and move the focused window to it
  * The primary display is marked with `★`
  * `Next Display` and `Previous Display` are also available
  * The window keeps its relative position and size where possible, then is constrained to the target display's visible area
* `wm` includes **Move to Main Display** and **Choose Display…**. Choosing the latter opens the same dynamic `wms` display list. The unassigned **Send to Main Display** Hotkey can be configured in Alfred's Workflow Editor.

Display names and IDs are read afresh whenever `wms` runs, so reconnecting a display needs no workflow restart. Native macOS full-screen windows are intentionally not moved.

### Keyboard shortcuts are suggestions:

*  ⇧↓ : Move to next screen
*  ⇧↑ : Move to previous screen
*  ^⌥M : Maximize
*  ^⌥C : Center Window
*  ^⌥← : Window to the left screen
*  ^⌥→ : Window to the right screen
*  ⌃⌥R : Reset Window
*  ⇧⌥W : Scale up window
*  ⇧⌥S : Scale down window
*  ⇧⌥D : Scale up right side of the window
*  ⇧⌥A : Scale up left side of the window
*  ⌥ A : Move window left
*  ⌥ D : Move window right
*  ⌥ W : Move window up
*  ⌥ S : Move window down
