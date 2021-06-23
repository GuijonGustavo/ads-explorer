import ads


#ads.config.token = 'my token'

class author:
    def __init__(self, name=None, orcid=None):
        self.name = name
        self.orcid = orcid

        if name == None and orcid == None:
            print('WARNING: No identifier supplied, please supply either the name, the ORCID or both')

    #comprobar si nombre es iterable y si no si es un string

    def papers(self):
        name = self.name
        orcid = self.orcid
        if not isinstance(name, str) and name != None:
            papers_name = list(ads.SearchQuery(author=name[0]))
            for kname in range(len(name)):
                papers_name += list(ads.SearchQuery(author=name[kname]))
        else:
            papers_name = list(ads.SearchQuery(author=name))

        papers_orcid = list(ads.SearchQuery(orcid=orcid))

        papers_all = papers_name + papers_orcid

        return papers_all
camps = author(['camps,a','camps-farina'])
camps_papers = camps.papers()
print(camps_papers[0].title)