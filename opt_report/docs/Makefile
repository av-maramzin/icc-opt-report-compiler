FILE = dissertation

build: $(FILE).tex
	pdflatex $(FILE)
	pdflatex $(FILE)
	bibtex $(FILE)
	pdflatex $(FILE)
	pdflatex $(FILE)
	pdflatex $(FILE)

clean:
	$(RM) *.aux *.bbl *.blg *.dvi *.idx *.log *.lol *.out *.spl *.t1 *.toc *~
	$(RM) src/*.aux src/*.log
