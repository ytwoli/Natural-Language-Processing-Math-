# Requirements
Semantic search in mathematics typically requires a combination of mathematical representation, semantic understanding, and search techniques. 
+ **One of the key requirements**: Understanding of the mathematical formulae it contains. This is only possible if we understand the meaning of the symbols in a formula.
+ **The Pipline**: 
  
  <img width="703" alt="image" src="https://github.com/ytwoli/Natural-Language-Processing-Math-/assets/75457507/983b07ee-6aea-4572-bd87-8ef8d72c3c91">
  
  + ***LaTeXML***
    LATEXML can be used to convert TEX/LATEX documents into HTML files. It aims at preserving both semantics and the visual representation of the original documents.
  + ***LLaMaPUn***
  The LLaMaPUn (Language and Mathematics Processing and Understanding) library contains many tools required for natural language processing of mathematical documents.
      > ***Document Narrative Model (DNM)***: A DNM contains a plaintext representation of the HTML file and supports mappings between the plaintext and the original Document Object Model (DOM).

      > ***Document Object Model (DOM)***: It is a programming interface that represents the structure of an HTML or XML document as a tree-like structure, where each node in the tree represents a part of the document (e.g., an element, attribute, or text). The DOM provides a way to access, manipulate, and update the content, structure, and style of a document
  + ***Senna***
  
    Senna is a natural language processing (NLP) toolkit, which  It provides various language processing functionalities and tools for tasks such as tokenization, part-of-speech tagging, named entity recognition, syntactic parsing, and semantic role labeling.
      > ***Part-of-Speech(POS)***: Senna includes a part-of-speech tagger that assigns grammatical tags to each word in a sentence. These tags indicate the word's syntactic category, such as noun, verb, adjective, etc. POS tagging is useful for various NLP tasks, including information extraction, text classification, and language understanding.
      
      > ***Syntactic Parsing***: Senna provides a syntactic parser that analyzes the grammatical structure of sentences. It generates parse trees or dependency graphs that represent the syntactic relationships between words. Syntactic parsing is crucial for tasks like sentence understanding, question answering, and machine translation.

# Declarations
There are three different objects our spotter should find: Declarations, restrictions, and identifiers. A declaration should contain a reference to the declarational phrase and the set of identifiers it declares. 
## Restrictions
  + ***Conditions***: often refers to logical constraints or requirements that must be met for certain actions or operations to occur. E.g., $Let \ x\in\mathbb{R}$
  + ***Types***: Type restrictions refer to constraints or limitations imposed on the data types of variables, attributes, or fields in a programming language or database. E.g., $Let \ x \ be \ a \ real \ number$. And definite type restrictions often start with the definite article “the”.
## Indetifiers
  + ***Character***: the most simple type of identifier, like e.g. " $Let \ p \ be \ a \ prime \ number$ ", where " $p$ "is clearly the identifier.
  + ***Indeved Idenridiers***: e.g. like " $x^1, \ x^2 \dots$ " or variables like " $a_i$ "
  + ***Structures Identifiers***: e.g. like " $Let \textlangle G, o \textrangle \ be \ a \ group$ ". Here we know that " $G$ " is onle a $set$, and a $group$ is actually refers to $\textlangle G,o\textrangle$. So this declaration is basicall a short form of " $Let \ \mathbb{G} = \textlangle G, o\textrangle$ \ be \ a\ group."

## Types of Declarations
  + ***Universal***:
  + ***Exitential***:
  + ***Definite***:
