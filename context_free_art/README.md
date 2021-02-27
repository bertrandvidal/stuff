# Remember ...

Remember your few months of learning 3d? For some reason the one thing that has followed me through the years are "context-free generative grammar to create natural system". For some reason I have the image of a root system rendered in 3d that was generated using simple rules. E.g. 'a > ab' / 'ab' > 'c' are the grammar rules that tell you that if you encounter 'a' it will be replaced by 'a' and 'ab' will be replaced with 'c'.

# Examples

- https://gist.github.com/FLamparski/717bb8bd708dae6d4d48
- http://www.nltk.org/howto/generate.html

# What to do with that?

Generate images!
Start with a black RGB image, your grammar takes a pixel `[(x,y), (R, G, B)]` and transform it to `[(x', y'), (R', G', B')]` ... and that's it I hope it'll look nice. And maybe make GIFs out of it!? I should probably look at existing libraries that help you define grammars
