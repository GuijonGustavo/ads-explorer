import ads
import itertools
from metaphone import doublemetaphone
import numpy as np
import pandas as pd

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


class PapersManager:
    """
    Manager of a list of papers

    Attributes
    ----------
    paper_list : list
        Resulting paper list by SearchQuery method of ADS package

    Methods
    -------
    TBW
    """

    def __init__(self, papers_list):
        """
        Parameters
        ----------
        papers_list : list
             List of papers
        """
        self.papers_list = papers_list
        self.papers_df = self.make_pandas()
        self.lookup_dict = ({}, {})
        self.set_lookup_dir()

    def make_pandas(self):
        """
        make a pandas dataframe from a papers list
        """
        columns = self.papers_list[0]._raw.keys()
        papers_df = pd.DataFrame(columns=columns)
        for paper in self.papers_list:
            papers_df = papers_df.append(paper._raw, ignore_index=True)
        # papers_df.set_index('id', inplace=True)
        return papers_df

    def add_combinations_to_directory(self, name_tuple_list, person_id):
        """
        Add all the combinations for a name to the lookup directory
        """
        for name_tuple in name_tuple_list:
            concat_name = generate_normalized_name(name_tuple)
            metaphone_tuple = doublemetaphone(concat_name)
            if metaphone_tuple[0] in self.lookup_dict[0]:
                if not person_id in self.lookup_dict[0][metaphone_tuple[0]]:
                    self.lookup_dict[0][metaphone_tuple[0]].append(person_id)
            else:
                self.lookup_dict[0][metaphone_tuple[0]] = [person_id]
            if metaphone_tuple[1] in self.lookup_dict[1]:
                if not person_id in self.lookup_dict[1][metaphone_tuple[1]]:
                    self.lookup_dict[1][metaphone_tuple[1]].append(person_id)
            else:
                self.lookup_dict[1][metaphone_tuple[1]] = [person_id]

    def add_person_to_lookup_directory(self, person_id, name_tuple):
        """
        Add a person id (paper id) and the name to the lookup directory
        """
        combs = generate_combinations(name_tuple)
        self.add_combinations_to_directory(combs, person_id)

    def match_name(self, name_tuple):
        """
        Check if a name is on the lookup directory and returns the match list
        """
        match_list = []
        combinations = generate_combinations(name_tuple)
        for comb_tuple in combinations:
            concat_name = generate_normalized_name(comb_tuple)
            metaphone_tuple = doublemetaphone(concat_name)
            if metaphone_tuple[0] in self.lookup_dict[0]:
                match_list.append(
                    (concat_name, self.lookup_dict[0][metaphone_tuple[0]]))
        # Iterate through all matches and check for single result tuples
        # Ensure that the singe result tuples are pointing to the same id
        # If not or no single result tuple exists, return 'None'
        unique_id = None
        for match_tuple in match_list:
            if len(match_tuple[1]) == 1:
                if unique_id is not None:
                    if unique_id != match_tuple[1][0]:
                        unique_id = None
                        break
                else:
                    unique_id = match_tuple[1][0]
        return unique_id, match_list

    def set_lookup_dir(self):
        """
        Set lookup directory for author search
        """
        for i in range(len(self.papers_df)):
            row = self.papers_df.iloc[i]
            authors = row['author']
            id_paper = row.name
            for author in authors:
                author_c = [normalize(word.strip('.,'))
                            for word in author.split(' ')]
                self.add_person_to_lookup_directory(id_paper, author_c)

    def search_author(self, names):
        """
        Search name(s) in the abstract

        Parameters
        ----------
        names : str or list
            name or list of names to search in the paper list

        """
        if isinstance(names, str):
            name_tuple = normalize(names).split(' ')
            _, match_list = self.match_name(name_tuple)
            match_id = []
            for elem in match_list:
                match_id += elem[1]
        else:
            match_id = []
            for name in names:
                name_tuple = normalize(name).split(' ')
                _, match_list = self.match_name(name_tuple)
                for elem in match_list:
                    match_id += elem[1]
        match_id_set = set(match_id)
        if len(match_id_set) != 0:
            papers_list = [self.papers_list[i] for i in match_id_set]
            return PapersManager(papers_list)
        else:
            print('Not match found')
            return None
        # return self.papers_df.loc[match_id_set]

    def search_word(self, words, logical_op='and'):
        """
        Search word(s) in the abstract

        Parameters
        ----------
        words : str or list
            Word or list of words to search in abstract

        logical_op : str
            Logical operation for a list of words, defaul:'and'
        """
        if 'abstract' not in self.papers_df.columns:
            print('No abstract field found')
            return None
        if isinstance(words, str):
            mask = self.papers_df['abstract'].str.contains(words,
                                                           case=False)
        else:
            masks = [[self.papers_df['abstract'].str.contains(word,
                                                              case=False)]
                     for word in words]
            mask = np.ones_like(masks[0][0])
            if logical_op == 'and':
                for submask in masks:
                    mask = mask & submask[0]
            elif logical_op == 'or':
                for submask in masks:
                    mask = mask | submask
        if not mask.sum() == 0:
            papers_list = []
            for i, val in enumerate(mask):
                if val:
                    papers_list.append(self.papers_list[i])
            return PapersManager(papers_list)
        else:
            print('Not match found')
            return None
        # return self.papers_df.loc[mask]

    def search_year(self, years):
        """
        Search papers by year
        """
        if isinstance(years, int):
            mask = self.papers_df['year'].values == str(years)
        else:
            masks = [self.papers_df['year'].values == str(year)
                     for year in years]
            print(masks)
            mask = np.zeros_like(masks[0][0])
            for submask in masks:
                mask = mask | submask
        if not mask.sum() == 0:
            papers_list = []
            for i, val in enumerate(mask):
                if val:
                    papers_list.append(self.papers_list[i])
            return PapersManager(papers_list)
        else:
            print('Not match found')
            return None
        # return self.papers_df.loc[mask]

    def get_author_set(self):
        """
        Get author set from the papers list
        """
        if 'author' not in self.papers_df.columns:
            print('No author field found')
            return None
        authors_list = [author
                        for row in self.papers_df['author'].iteritems()
                        for author in row[1]]
        authors_list_clean = [normalize(author) for author in authors_list]
        authors_set = set(authors_list_clean)
        return authors_set

    def custom_output(self, fields, explicit=[], auth_num=None):
        """
        Generates a custom output in a particular format
        """
        if fields is None:
            print('No output fields specified, no output generated')
            return
        datafr = self.papers_df
        if isinstance(fields, str):
            for elem in list(datafr[fields]):
                print(f'· {elem[0]}')
        else:
            for kel in range(len(list(datafr[fields[0]]))):
                for kf in range(len(fields)):
                    elem = datafr[fields[kf]][kel]
                    if fields[kf] in explicit:
                        fname = fields[kf]+': '
                    else:
                        fname = ''
                    if isinstance(elem, list):
                        if len(elem) == 1:
                            print(f'{fname}{elem[0]}')
                        else:
                            print(fname+', '.join(elem))
                    else:
                        print(f'{fname}{elem}')
                    # print(datafr[fields[kf]][kel])
                    # print('')
                print('\n')

    def add_paper(self, bibcode):
        """
        Add a paper to the database
        """
        fl = ['abstract', 'author', 'id', 'year',
              'ack', 'aff', 'alternate_bibcode', 'alternate_title',
              'arxiv_class', 'citation_count', 'bibcode', 'bibgroup',
              'copyright', 'data', 'database', 'doctype', 'doi', 'identifier',
              'indexstamp', 'first_author', 'grant', 'issue', 'keyword',
              'page', 'property', 'pub', 'pubdate', 'read_count', 'reference',
              'citation', 'title', 'vizier', 'volume', 'orcid_pub',
              'orcid_user', 'orcid_other', 'metrics', 'bibtex']
        new_paper = list(ads.SearchQuery(bibcode=bibcode, fl=fl))
        self.papers_list += new_paper
        self.papers_df = self.make_pandas()
        self.lookup_dict = ({}, {})
        self.set_lookup_dir()

    def remove_paper(self, bibcode):
        """
        Remove a paper to the database
        """
        mask = self.papers_df.bibcode == bibcode
        idx = (self.papers_df.index[mask]).values[0]
        self.papers_list.pop(idx)
        self.papers_df = self.make_pandas()
        self.lookup_dict = ({}, {})
        self.set_lookup_dir()


def normalize(string):
    """
    Replace words with accent mark
    """
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("à", "a"),
        ("è", "e"),
        ("ù", "u"),
    )
    for vowel_w_acc, vowel_wo_acc in replacements:
        string = string.replace(vowel_w_acc,
                                vowel_wo_acc).replace(vowel_w_acc.upper(),
                                                      vowel_wo_acc.upper())
    return string


def clean_author_list(author_list):
    """
    Clean author list from duplicate entry
    """
    author_list_clean = [normalize(author) for author in author_list]
    return set(author_list_clean)


def generate_normalized_name(name_tuple):
    """
    Generates a normalized name (without whitespaces and lowercase)
    """
    name_arr = list(name_tuple)
    name_arr.sort()
    name_str = ''.join(name_arr)
    return name_str.lower()


def generate_combinations(name_tuple):
    """
    Generates all the possible combinations for a name
    """
    perms = []
    perms.append(name_tuple)
    i = len(list(name_tuple))-1
    while i > 0:
        perms.extend(itertools.combinations(name_tuple, i))
        i -= 1
    return perms
