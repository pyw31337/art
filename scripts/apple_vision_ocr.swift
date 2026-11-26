import Foundation
import Vision
import CoreGraphics
import ImageIO

guard CommandLine.arguments.count > 1 else {
    print("[]")
    exit(0)
}

let imagePath = CommandLine.arguments[1]
let fullPath = (imagePath as NSString).expandingTildeInPath
let fileUrl = URL(fileURLWithPath: fullPath)

guard let imageSource = CGImageSourceCreateWithURL(fileUrl as CFURL, nil),
      let cgImage = CGImageSourceCreateImageAtIndex(imageSource, 0, nil) else {
    print("[]")
    exit(0)
}

let request = VNRecognizeTextRequest { (request, error) in
    guard let observations = request.results as? [VNRecognizedTextObservation] else {
        print("[]")
        return
    }
    let strings = observations.compactMap { $0.topCandidates(1).first?.string }
    if let jsonData = try? JSONSerialization.data(withJSONObject: strings, options: []),
       let jsonStr = String(data: jsonData, encoding: .utf8) {
        print(jsonStr)
    } else {
        print("[]")
    }
}
request.recognitionLevel = .accurate
request.recognitionLanguages = ["ko-KR", "en-US", "fr-FR", "de-DE", "es-ES", "it-IT"]

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
} catch {
    print("[]")
}
