import ads


#ads.config.token = 'my token'

class author:
    def __init__(self, name, orcid=None):
        self.name = name
        self.orcid = orcid

    #comprobar si nombre es iterable y si no si es un string

    def papers(self):
        name = self.name
        orcid = self.orcid
        if not isinstance(name, str):
            papers_name = list(ads.SearchQuery(author=name[0]))
            for kname in range(len(name)):
                papers_name += list(ads.SearchQuery(author=name[kname]))
        else:
            papers_name = list(ads.SearchQuery(author=name))

        papers_orcid = list(ads.SearchQuery(orcid=orcid))

        papers_all = papers_name + papers_orcid

        return papers_all