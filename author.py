import ads


#ads.config.token = 'my token'
#TODO:
# - Implementar el token como variable global para el caso donde se pone manualmente
# - Gestion de caracteres especiales en nombres
# - Poner label al autor para identificar cuando se comparen 
# (por default el primer valor en name o el autor que salga en una busqueda con el ORCID)
# - Filtrar por defecto solo con refereo y sin proceedings
# - El metodo actual de contar citas al llamar a papers() ha de ser cambiado: el resultado del query 
# ha de pasarse a la clase de lista de papers, la cual se guarda como variable interna. La funcion de 
# contar citas entonces usa el dataframe directamente

class author:
    def __init__(self, name=None, orcid=None):
        self.name = name
        self.orcid = orcid

        if name == None and orcid == None:
            print('WARNING: No identifier supplied, please supply either the name, the ORCID or both')
        
        self.all_papers = None
        self.papers_fauth = None
        self.papers_nauth = None
        self.ncite_all = None
        self.ncite_fauth = None
        self.ncite_nauth = None
    #comprobar si nombre es iterable y si no si es un string

    def papers(self):
        if self.all_papers == None:
            name = self.name
            orcid = self.orcid
            if not isinstance(name, str) and name != None:
                papers_name = list(ads.SearchQuery(author=name[0]))
                papers_name_id = [x.id for x in papers_name]
                for kname in range(1,len(name)):
                    papers_kname = list(ads.SearchQuery(author=name[kname]))
                    for pkn in papers_kname:
                        if pkn.id not in papers_name_id:
                            papers_name.append(pkn)
                            papers_name_id.append(pkn.id)
            else:
                papers_name = list(ads.SearchQuery(author=name))
                papers_name_id = [x.id for x in papers_name]

            if orcid != None:
                papers_orcid = list(ads.SearchQuery(orcid=orcid))
                for porc in papers_orcid:
                    if porc.id not in papers_name_id:
                        papers_name.append(pkn)
                        papers_name_id.append(pkn.id)
            
            self.ncite_all = [x.citation_count for x in papers_name]
            self.all_papers = papers_name


        return self.all_papers
    
    def papers_first(self):
        if self.papers_fauth == None:
            name = self.name
            orcid = self.orcid
            if not isinstance(name, str) and name != None:
                papers_name = list(ads.SearchQuery(first_author=name[0]))
                papers_name_id = [x.id for x in papers_name]
                for kname in range(1,len(name)):
                    papers_kname = list(ads.SearchQuery(first_author=name[kname]))
                    for pkn in papers_kname:
                        if pkn.id not in papers_name_id:
                            papers_name.append(pkn)
                            papers_name_id.append(pkn.id)
            else:
                papers_name = list(ads.SearchQuery(first_author=name))
                papers_name_id = [x.id for x in papers_name]
            
            if orcid != None and name == None:
                print('Sorry, ADS does not have the functionality to search by ORCID and specifying author position, please add a name to be able to do this')
                return None
            elif orcid != None:
                papers_orcid = list(ads.SearchQuery(first_name=name, orcid=orcid))

                for porc in papers_orcid:
                    if porc.id not in papers_name_id:
                        papers_name.append(pkn)
                        papers_name_id.append(pkn.id)

            self.ncite_fauth = [x.citation_count for x in papers_name]
            self.papers_fauth = papers_name


        return self.papers_fauth


    def papers_not_first(self):
        if self.papers_nauth == None:
            name = self.name
            orcid = self.orcid
            if not isinstance(name, str) and name != None:
                papers_name_1 = list(ads.SearchQuery(first_author=name))
                papers_name_1_id = [x.id for x in papers_name_1]
                papers_name_2 = list(ads.SearchQuery(author=name))
                papers_name_2_id = [x.id for x in papers_name_2]

                papers_name = [x for x in papers_name_2 if papers_name_2_id[papers_name_2.index(x)] not in papers_name_1_id]
                papers_name_id = [x for x in papers_name_2_id if x not in papers_name_1_id]

                for kname in range(1,len(name)):
                    papers_kname_1 = list(ads.SearchQuery(first_author=name))
                    papers_kname_1_id = [x.id for x in papers_name_1]

                    papers_kname_2 = list(ads.SearchQuery(author=name))
                    papers_kname_2_id = [x.id for x in papers_name_2]

                    papers_kname = [x for x in papers_name_2 if papers_name_2_id[papers_name_2.index(x)] not in papers_name_1_id]

                    for pkn in papers_kname:
                        if pkn.id not in papers_name_id:
                            papers_name.append(pkn)
                            papers_name_id.append(pkn.id)
            else:
                papers_name_1 = list(ads.SearchQuery(first_author=name))
                papers_name_1_id = [x.id for x in papers_name_1]

                papers_name_2 = list(ads.SearchQuery(author=name))
                papers_name_2_id = [x.id for x in papers_name_2]

                papers_name = [x for x in papers_name_2 if papers_name_2_id[papers_name_2.index(x)] not in papers_name_1_id]
                papers_name_id = [x for x in papers_name_2_id if x not in papers_name_1_id]
            
            if orcid != None and name == None:
                print('Sorry, ADS does not have the functionality to search by ORCID and specifying author position, please add a name to be able to do this')
                return None
            elif orcid != None:
                papers_orcid_1 = list(ads.SearchQuery(orcid=orcid))
                papers_orcid_1_id = [x.id for x in papers_orcid_1]

                papers_orcid_2 = list(ads.SearchQuery(orcid=orcid))
                papers_orcid_2_id = [x.id for x in papers_orcid_2]

                papers_orcid = [x for x in papers_orcid_2 if papers_orcid_2_id[papers_orcid_2.index(x)] not in papers_orcid_1_id]
                papers_orcid_id = [x.id for x in papers_orcid]

                for porc in papers_orcid:
                    if porc.id not in papers_name_id:
                        papers_name.append(pkn)
                        papers_name_id.append(pkn.id)

            self.ncite_nauth = [x.citation_count for x in papers_name]
            self.papers_nauth = papers_name


        return self.papers_nauth

    def cite_number(self):
        if self.ncite_all == None:
            not_used = self.papers()
        
        return sum(self.ncite_all)
    
    def collaboration(self,author_2):
        if self.papers_fauth == None:
            papers_a1_first = self.papers_first()
            papers_a1_first_id = [x.id for x in papers_a1_first]
        if self.papers_nauth == None:
            papers_a1_notfirst = self.papers_not_first()
            papers_a1_notfirst_id = [x.id for x in papers_a1_notfirst]
        if self.all_papers == None:
            papers_a1 = papers_a1_first + papers_a1_notfirst
            papers_a1_id = [x.id for x in papers_a1]
        
        if author_2.papers_fauth == None:
            papers_a2_first = author_2.papers_first()
        if author_2.papers_nauth == None:
            papers_a2_notfirst = author_2.papers_not_first()
            papers_a2_notfirst_id = [x.id for x in papers_a2_notfirst]
        if author_2.all_papers == None:
            papers_a2 = papers_a2_first + papers_a2_notfirst
            papers_a2_id = [x.id for x in papers_a2]
        


        common = [x for x in papers_a2 if x.id in papers_a1_id]

        common_a1_first = [x for x in papers_a1_first if x.id in papers_a2_id]
        common_a2_first = [x for x in papers_a2_first if x.id in papers_a1_id]
        common_nonefirst = [x for x in papers_a1_notfirst if x.id in papers_a2_notfirst_id]

        cite_common = [x.citation_count for x in common]
        cite_a1_first = [x.citation_count for x in common_a1_first]
        cite_a2_first = [x.citation_count for x in common_a2_first]
        cite_nonefirst = [x.citation_count for x in common_nonefirst]


        print(f'Collaboration stats between {self.name} and {author_2.name}:') #CHANGE TO AUTHOR LABELS!!! BREAKS IF NAME NOT SUPPLIED OR LIST OF NAMES!!
        print(f'Papers in common: {len(common)}')
        print(f'Papers in common where {self.name} is first author: {len(common_a1_first)}')
        print(f'Papers in common where {author_2.name} is first author: {len(common_a2_first)}')
        print(f'Papers in common where neither is first author: {len(common_nonefirst)}')
        print('')
        print(f'Citations of common papers: {sum(cite_common)}')
        print(f'Citations of common papers where {self.name} is first author: {sum(cite_a1_first)}')
        print(f'Citations of common papers where {author_2.name} is first author: {sum(cite_a2_first)}')
        print(f'Citations of common papers where neither is first author: {sum(cite_nonefirst)}')


#camps = author(['camps,artemi','camps-farina, a'])
#camps_papers = camps.papers()
#print(camps_papers[0].title)