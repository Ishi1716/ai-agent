from pdf_tool import search_pdf


question = input("Ask something about the PDF: ")


result = search_pdf(question)


print("\nRelevant PDF information:\n")
print(result)