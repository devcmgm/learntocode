### Libraries Needed for XML Processing in C

To process XML in C, the most commonly used library is **libxml2**. It is a robust, open-source XML parsing library that supports parsing, validation, XPath queries, XSLT transformations, and more. It is part of the GNOME project but is widely adopted across platforms (Linux, Windows, macOS).

- **Installation**:
  - On Ubuntu/Debian: `sudo apt-get install libxml2-dev`
  - On macOS (with Homebrew): `brew install libxml2`
  - On Windows: Download from the official site or use vcpkg/MSYS2.
  
- **Compilation**: When building your C program, link against the library using `-lxml2` (e.g., `gcc example.c -o example -lxml2`).

Other alternatives include:
- **Expat**: A lightweight, stream-oriented XML parser (header: `<expat.h>`, link: `-lexpat`).
- **TinyXML**: A simple DOM parser for small projects (but less feature-rich).

The example below uses **libxml2** for a basic DOM (Document Object Model) parser that reads an XML file, traverses the tree, and prints node names and content.

### C Code Example: Simple XML Parser

This example parses a sample XML file (`sample.xml`) and prints the names and text content of all elements. Assume `sample.xml` contains:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
    <person name="Alice">
        <age>30</age>
        <city>New York</city>
    </person>
    <person name="Bob">
        <age>25</age>
        <city>London</city>
    </person>
</root>
```

```c
#include <stdio.h>
#include <libxml/parser.h>
#include <libxml/tree.h>

/**
 * Recursively traverses the XML tree and prints node details.
 * @param node The current XML node.
 */
static void print_element_names(xmlNode *node) {
    xmlNode *cur_node = NULL;
    for (cur_node = node; cur_node; cur_node = cur_node->next) {
        if (cur_node->type == XML_ELEMENT_NODE) {
            printf("Node name: %s\n", cur_node->name);
            
            // Print text content if it's a leaf node
            xmlChar *content = xmlNodeGetContent(cur_node);
            if (content != NULL) {
                printf("  Content: %s\n", content);
                xmlFree(content);
            }
            
            // Recurse into children
            print_element_names(cur_node->children);
        }
    }
}

int main(int argc, char **argv) {
    if (argc != 2) {
        printf("Usage: %s <xml_file>\n", argv[0]);
        return 1;
    }

    // Parse the XML file
    xmlDocPtr doc = xmlReadFile(argv[1], NULL, 0);
    if (doc == NULL) {
        fprintf(stderr, "Error: Could not parse '%s'\n", argv[1]);
        return 1;
    }

    // Get the root element
    xmlNodePtr root = xmlDocGetRootElement(doc);
    if (root == NULL) {
        fprintf(stderr, "Error: Empty document\n");
        xmlFreeDoc(doc);
        return 1;
    }

    printf("Root node: %s\n", root->name);
    print_element_names(root);

    // Cleanup
    xmlFreeDoc(doc);
    xmlCleanupParser();

    return 0;
}
```

### How It Works
1. **Headers**: `<libxml/parser.h>` for parsing functions, `<libxml/tree.h>` for tree traversal.
2. **Parsing**: `xmlReadFile()` loads and parses the XML into a document tree (`xmlDocPtr`).
3. **Traversal**: The `print_element_names()` function recursively walks the tree using `xmlNode` pointers, printing element names and content.
4. **Cleanup**: Always free the document with `xmlFreeDoc()` and clean up globals with `xmlCleanupParser()` to avoid memory leaks.
5. **Running**: Compile with `gcc xml_parser.c -o xml_parser -lxml2`, then run `./xml_parser sample.xml`. Output:
   ```
   Root node: root
   Node name: person
     Node name: name
       Content: Alice
     Node name: age
       Content: 30
     Node name: city
       Content: New York
   Node name: person
     Node name: name
       Content: Bob
     Node name: age
       Content: 25
     Node name: city
       Content: London
   ```

This is a basic starting point. For more advanced features (e.g., XPath), extend with `<libxml/xpath.h>`. Refer to the libxml2 documentation for details.
