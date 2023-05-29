# Requirements
Semantic search in mathematics typically requires a combination of mathematical representation, semantic understanding, and search techniques. 
+ **One of the key requirements**: Understanding of the mathematical formulae it contains. This is only possible if we understand the meaning of the symbols in a formula.
+ **The Pipline**: 
  
  <img width="703" alt="image" src="https://github.com/ytwoli/Natural-Language-Processing-Math-/assets/75457507/983b07ee-6aea-4572-bd87-8ef8d72c3c91">
  
  * *LaTeXML*
  * *LLaMaPUn*
      > *Document Narrative Model (DNM)*

      > *Document Object Model (DOM)*
  * *Senna*
      > *Part-of-Speech(POS)*
      > *Syntactic Parsing*

# Declarations
There are three different objects our spotter should find: Declarations, restrictions, and identifiers. A declaration should contain a reference to the declarational phrase and the set of identifiers it declares. 
## Restrictions
  + ***Conditions***
  + ***Types***
## Indetifiers
  + ***Character***: the most simple type of identifier, like e.g. " $Let \ p \ be \ a \ prime \ number$ ", where " $p$ "is clearly the identifier.
  + ***Indeved Idenridiers***: e.g. like " $x^1, \ x^2 \dots$ " or variables like " $a_i$ "
  + ***Structures Identifiers***: e.g. like " $Let \textlangle D, o \textrangle \ be \ a \ group$ ". Here we know that " $G$ " is onle a $set$, and a $group$ is actually refers to $\textlangleG,o\textrangle$. So this declaration is basicall a short form of " $Let \ \mathbb{G} = \textlangleG, o\textrangle$ \ be \ a\ group."
