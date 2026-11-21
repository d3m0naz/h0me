import Cocoa
import WebKit
let args = CommandLine.arguments
let isWeb = args[1].hasPrefix("http"); let url = isWeb ? URL(string: args[1])! : URL(fileURLWithPath: args[1]); let out = args[2]
let w = CGFloat(Double(args[3])!), h = CGFloat(Double(args[4])!)
let dark = args.count > 5 && args[5] == "dark"
let app = NSApplication.shared
app.appearance = NSAppearance(named: dark ? .darkAqua : .aqua)
class D: NSObject, WKNavigationDelegate {
  func webView(_ v: WKWebView, didFinish n: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + 4.5) {
      let c = WKSnapshotConfiguration(); c.rect = CGRect(x:0,y:0,width:w,height:h)
      v.takeSnapshot(with: c) { img, e in
        let rep = NSBitmapImageRep(data: img!.tiffRepresentation!)!
        try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: out))
        exit(0) }
    }
  }
}
let win = NSWindow(contentRect: NSRect(x:0,y:0,width:w,height:h), styleMask: [.borderless], backing: .buffered, defer: false)
win.appearance = app.appearance
let v = WKWebView(frame: win.contentView!.bounds); win.contentView!.addSubview(v)
let d = D(); v.navigationDelegate = d
if isWeb { v.load(URLRequest(url: url)) } else { v.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent().deletingLastPathComponent()) }
DispatchQueue.main.asyncAfter(deadline: .now() + 30) { exit(1) }
app.run()
