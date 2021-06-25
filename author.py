from paper_manager import PapersManager
import ads


#ads.config.token = 'my token'
# TODO:
# - Implementar el token como variable global para el caso donde se pone manualmente
# - Poner label al autor para identificar cuando se comparen
# (por default el primer valor en name o el autor que salga en una busqueda con el ORCID)
# - H factor y otras metricas
# - Funciones a añadir: report: calcula el num de articulos de cada tipo, año mas productivo,
# grafico de productividad/citas por tiempo, gente con la que mas colabora/con mas citas, red de colaboradores

fl = ['ack',
      'aff',
      'alternate_bibcode',
      'alternate_title',
      'arxiv_class',
      'citation_count',
      'bibcode',
      'bibgroup',
      'copyright',
      'data',
      'database',
      'doctype',
      'doi',
      'identifier',
      'indexstamp',
      'first_author',
      'grant',
      'issue',
      'keyword',
      'page',
      'property',
      'pub',
      'pubdate',
      'read_count',
      'reference',
      'citation',
      'title',
      'vizier',
      'volume',
      'orcid_pub',
      'orcid_user',
      'orcid_other',
      'metrics',
      'bibtex',
      'abstract',
      'author',
      'id',
      'year']


class author:
    """
    This class defines an author as a result of inputting one or more names that the author uses in their papers.
    It can then be used to perform searches for all the papers they have authored, those in which they are first author
    or those in which they are not the first author. The results of the querys are saved as a PapersManager instance.

    name (string/list) : The name or list of names to be parsed to ADS to search for papers
    orcid (string)     : The ORCID identifier associated with the author
    refereed (bool)    : Whether to include only refereed articles, by default it is True
    fl                 : List of parameters that ADS will provide, by default it is all the parameters. It can be reduced
                         so that the querys are faster for intensive use
    """

    def __init__(self, name=None, orcid=None, refereed=True, fl=fl):
        self.name = name
        self.orcid = orcid
        self.fl = fl
        if refereed == True:
            self.kw = {'doctype': 'article'}
        else:
            self.kw = {}

        if name == None and orcid == None:
            print(
                'WARNING: No identifier supplied, please supply either the name, the ORCID or both')
        elif name == None:
            print('WARNING: Only the ORCID was supplied. Due to how the ADS API works any function where'
                  'author position is necessary will break, i.e., papers_first, papers_not_first, collaboration...')

        self.all_papers = None
        self.papers_fauth = None
        self.papers_nauth = None
        self.ncite_all = None
        self.ncite_fauth = None
        self.ncite_nauth = None
    # comprobar si nombre es iterable y si no si es un string

    def papers(self):
        """
        Searches for all papers from the author
        """
        if self.all_papers == None:
            name = self.name
            orcid = self.orcid
            if not isinstance(name, str) and name != None:
                papers_name = list(ads.SearchQuery(
                    author=name[0], fl=self.fl, **self.kw))
                papers_name_id = [x.id for x in papers_name]
                for kname in range(1, len(name)):
                    papers_kname = list(ads.SearchQuery(
                        author=name[kname], fl=self.fl, **self.kw))
                    for pkn in papers_kname:
                        if pkn.id not in papers_name_id:
                            papers_name.append(pkn)
                            papers_name_id.append(pkn.id)
            elif name != None:
                papers_name = list(ads.SearchQuery(
                    author=name, fl=self.fl, **self.kw))
                papers_name_id = [x.id for x in papers_name]
            else:
                papers_name = []
                papers_name_id = []

            if orcid != None:
                papers_orcid = list(ads.SearchQuery(
                    orcid=orcid, fl=self.fl, **self.kw))
                for porc in papers_orcid:
                    if porc.id not in papers_name_id:
                        papers_name.append(porc)
                        papers_name_id.append(porc.id)

            self.ncite_all = [x.citation_count for x in papers_name]
            self.all_papers = PapersManager(papers_name)

        return self.all_papers

    def papers_first(self):
        """
        Searches for all papers where the author is the first author
        """
        if self.papers_fauth == None:
            name = self.name
            orcid = self.orcid
            if not isinstance(name, str) and name != None:
                papers_name = list(ads.SearchQuery(
                    first_author=name[0], fl=self.fl, **self.kw))
                papers_name_id = [x.id for x in papers_name]
                for kname in range(1, len(name)):
                    papers_kname = list(ads.SearchQuery(
                        first_author=name[kname], fl=self.fl, **self.kw))
                    for pkn in papers_kname:
                        if pkn.id not in papers_name_id:
                            papers_name.append(pkn)
                            papers_name_id.append(pkn.id)
            elif name != None:
                papers_name = list(ads.SearchQuery(
                    first_author=name, fl=self.fl, **self.kw))
                papers_name_id = [x.id for x in papers_name]
            else:
                papers_name = []
                papers_name_id = []

            if orcid != None and name == None:
                print('Sorry, ADS does not have the functionality to search by ORCID and specifying author position, please add a name to be able to do this')
                return None
            elif orcid != None:
                papers_orcid = list(ads.SearchQuery(
                    first_name=name, orcid=orcid, fl=self.fl, **self.kw))

                for porc in papers_orcid:
                    if porc.id not in papers_name_id:
                        papers_name.append(porc)
                        papers_name_id.append(porc.id)

            self.ncite_fauth = [x.citation_count for x in papers_name]
            self.papers_fauth = PapersManager(papers_name)

        return self.papers_fauth

    def papers_not_first(self):
        """
        Searches for all papers where the author is NOT the first author
        """
        if self.papers_nauth == None:
            name = self.name
            orcid = self.orcid
            if not isinstance(name, str) and name != None:
                papers_name_1 = list(ads.SearchQuery(
                    first_author=name, fl=self.fl, **self.kw))
                papers_name_1_id = [x.id for x in papers_name_1]
                papers_name_2 = list(ads.SearchQuery(
                    author=name, fl=self.fl, **self.kw))
                papers_name_2_id = [x.id for x in papers_name_2]

                papers_name = [x for x in papers_name_2 if papers_name_2_id[papers_name_2.index(
                    x)] not in papers_name_1_id]
                papers_name_id = [
                    x for x in papers_name_2_id if x not in papers_name_1_id]

                for kname in range(1, len(name)):
                    papers_kname_1 = list(ads.SearchQuery(
                        first_author=name, fl=self.fl, **self.kw))
                    papers_kname_1_id = [x.id for x in papers_name_1]

                    papers_kname_2 = list(ads.SearchQuery(
                        author=name, fl=self.fl, **self.kw))
                    papers_kname_2_id = [x.id for x in papers_name_2]

                    papers_kname = [x for x in papers_name_2 if papers_name_2_id[papers_name_2.index(
                        x)] not in papers_name_1_id]

                    for pkn in papers_kname:
                        if pkn.id not in papers_name_id:
                            papers_name.append(pkn)
                            papers_name_id.append(pkn.id)
            elif name != None:
                papers_name_1 = list(ads.SearchQuery(
                    first_author=name, fl=self.fl, **self.kw))
                papers_name_1_id = [x.id for x in papers_name_1]

                papers_name_2 = list(ads.SearchQuery(
                    author=name, fl=self.fl, **self.kw))
                papers_name_2_id = [x.id for x in papers_name_2]

                papers_name = [x for x in papers_name_2 if papers_name_2_id[papers_name_2.index(
                    x)] not in papers_name_1_id]
                papers_name_id = [
                    x for x in papers_name_2_id if x not in papers_name_1_id]

            # if orcid != None and name == None:
             #   print('Sorry, ADS does not have the functionality to search by ORCID and specifying author position, please add a name to be able to do this')
              #  return None
            elif orcid != None:
                papers_orcid_1 = list(ads.SearchQuery(
                    orcid=orcid, fl=self.fl, **self.kw))
                papers_orcid_1_id = [x.id for x in papers_orcid_1]

                papers_orcid_2 = list(ads.SearchQuery(
                    orcid=orcid, fl=self.fl, **self.kw))
                papers_orcid_2_id = [x.id for x in papers_orcid_2]

                papers_orcid = [x for x in papers_orcid_2 if papers_orcid_2_id[papers_orcid_2.index(
                    x)] not in papers_orcid_1_id]
                papers_orcid_id = [x.id for x in papers_orcid]

                for porc in papers_orcid:
                    if porc.id not in papers_name_id:
                        papers_name.append(pkn)
                        papers_name_id.append(pkn.id)
            else:
                papers_name_1 = []
                papers_name_1_id = []

                papers_name_2 = []
                papers_name_2_id = []

                papers_name = []
                papers_name_id = []

            self.ncite_nauth = [x.citation_count for x in papers_name]
            self.papers_nauth = PapersManager(papers_name)

        return self.papers_nauth

    def cite_number(self):
        """
        Returns the total number of cites for the papers of the author.
        """
        if self.ncite_all == None:
            not_used = self.papers()

        return sum(self.ncite_all)

    def collaboration(self, author_2):
        """
        Computes the stats for the articles in common between two authors. Each of the authors is represented
        by an instance of the author class.
        """
        # ADD: average citation per group, graph of evolution of common papers per year
        if self.papers_fauth == None:
            papers_a1_first = self.papers_first()
            #papers_a1_first_id = [x.id for x in papers_a1_first]
        if self.papers_nauth == None:
            papers_a1_notfirst = self.papers_not_first()
            #papers_a1_notfirst_id = [x.id for x in papers_a1_notfirst]
        if self.all_papers == None:
            papers_a1 = papers_a1_first + papers_a1_notfirst
            papers_a1_id = [x.id for x in papers_a1]
        if self.name == None:
            self.name = self.papers_fauth.papers_df['author'][0][0]

        if author_2.papers_fauth == None:
            papers_a2_first = author_2.papers_first()
        if author_2.papers_nauth == None:
            papers_a2_notfirst = author_2.papers_not_first()
            papers_a2_notfirst_id = [x.id for x in papers_a2_notfirst]
        if author_2.all_papers == None:
            papers_a2 = papers_a2_first + papers_a2_notfirst
            papers_a2_id = [x.id for x in papers_a2]
        if author_2.name == None:
            author_2.name = author_2.papers_fauth.papers_df['author'][0][0]

        common = [x for x in papers_a2 if x.id in papers_a1_id]

        common_a1_first = [x for x in papers_a1_first if x.id in papers_a2_id]
        common_a2_first = [x for x in papers_a2_first if x.id in papers_a1_id]
        common_nonefirst = [
            x for x in papers_a1_notfirst if x.id in papers_a2_notfirst_id]

        cite_common = [x.citation_count for x in common]
        cite_a1_first = [x.citation_count for x in common_a1_first]
        cite_a2_first = [x.citation_count for x in common_a2_first]
        cite_nonefirst = [x.citation_count for x in common_nonefirst]

        # CHANGE TO AUTHOR LABELS
        print(f'Collaboration stats between {self.name} and {author_2.name}:')
        print(f'Papers in common: {len(common)}')
        print(
            f'Papers in common where {self.name} is first author: {len(common_a1_first)}')
        print(
            f'Papers in common where {author_2.name} is first author: {len(common_a2_first)}')
        print(
            f'Papers in common where neither is first author: {len(common_nonefirst)}')
        print('')
        print(f'Citations of common papers: {sum(cite_common)}')
        print(
            f'Citations of common papers where {self.name} is first author: {sum(cite_a1_first)}')
        print(
            f'Citations of common papers where {author_2.name} is first author: {sum(cite_a2_first)}')
        print(
            f'Citations of common papers where neither is first author: {sum(cite_nonefirst)}')


camps = author(['camps,artemi', 'camps-farina, a'])
camps_papers = camps.papers()
# print(camps_papers[0].title)
