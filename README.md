# refactoring_tool
A Refactoring tool in python that is able to detect following code smells:
1. Long Method/Function
In the context of this project, we define 15 Lines of Code as the threshold for a long
method/function. In other words, if a method/function contains 16 or more lines of code,
we will say the code smell Long Method/Function exists. Please notice that a blank line is
NOT considered as one line of code.
2. Long Parameter List
In the context of this homework, we define 3 Parameters as the threshold for a long
parameter list. In other words, if a method/function contains 4 or more parameters, we will
say this method/function has a long parameter list.
3. Duplicated Code
there are different types of duplicated code. In the context of
this homework, you will need to adopt a metrics-based approach. To be more specific, we
will use Jaccard Similarity.Second, IF duplicated code is detected (in the context of our project, it means two similar code
fragments executing the same functionality),  tool  is be able to refactor the duplicated
code
