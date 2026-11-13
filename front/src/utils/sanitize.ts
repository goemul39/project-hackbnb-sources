import DOMPurify from "dompurify"

/**
 * D7: clean room descriptions before injecting them as HTML.
 * Only basic tags are allowed, scripts and on* attributes are removed.
 */
const ALLOWED_TAGS = [
    "p", "br", "strong", "b", "em", "i", "u", "ul", "ol", "li",
    "blockquote", "h1", "h2", "h3", "h4", "h5", "h6", "a", "span",
]

const ALLOWED_ATTR = ["href", "title", "target", "rel"]

export const sanitizeDescription = (html: string | undefined | null): string => {
    if (!html) {
        return ""
    }

    return DOMPurify.sanitize(html, {
        ALLOWED_TAGS,
        ALLOWED_ATTR,
        ALLOW_DATA_ATTR: false,
        FORBID_TAGS: ["script", "style", "iframe", "object", "embed", "form", "input"],
        FORBID_ATTR: ["style", "onerror", "onload", "onclick"],
    })
}
