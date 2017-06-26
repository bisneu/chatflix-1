# coding: utf-8

from User import User
from numpy.random import randint
import numpy as np
from sklearn.cluster import KMeans

from movielens import load_movies, load_simplified_ratings


class Recommendation:

    def __init__(self):

        # Importe la liste des films
        # Dans la variable 'movies' se trouve la correspondance entre l'identifiant d'un film et le film
        # Dans la variables 'movies_list' se trouve les films populaires qui sont vus par les utilisateurs
        self.movies = load_movies()
        self.movies_list = []

        # Importe la liste des notations
        # Dans le tableau 'ratings' se trouve un objet avec un attribut 'movie' contenant l'identifiant du film, un
        # attribut 'user' avec l'identifiant de l'utilisateur et un attribut 'is_appreciated' pour savoir si oui ou non
        # l'utilisateur aime le film
        self.ratings = load_simplified_ratings()

        # Les utilisateurs du fichier 'ratings-popular-simplified.csv' sont stockés dans 'test_users'
        self.test_users = {}
        # Les utilisateurs du chatbot facebook seront stockés dans 'users'
        self.users = {}

        # Lance le traitement des notations
        self.process_ratings_to_users()

    # Traite les notations
    # Crée un utilisateur de test pour chaque utilisateur dans le fichier
    # Puis lui attribue ses films aimés et détestés
    def process_ratings_to_users(self):
        for rating in self.ratings:
            user = self.register_test_user(rating.user)
            if rating.is_appreciated is not None:
                if rating.is_appreciated:
                    user.good_ratings.append(rating.movie)
                else:
                    user.bad_ratings.append(rating.movie)
            elif rating.score is not None:
                user.ratings.append(rating)
            self.movies_list.append(rating.movie)

    # Cherche un id_film dans les "bad_ratings" de l'utilisateur donnée en argument et le renvoie
    def search_in_bad_ratings(user,movie):
        for movie_u in user.bad_ratings:
            if movie_u == movie:
                return (movie_u*-1)
        return 0

    # Cherche un id_ilm dans les "good_ratings de l'utilisateur donnée en argument et le renvoie
    def search_in_good_ratings(user,movie):
        for movie_u in user.good_ratings:
            if movie_u == movie:
                return movie_u
        return 0

    #Cherche un id_ilm dans les "neutral_ratings de l'utilisateur donnée en argument et le renvoie
    def search_in_neutral_ratings(user,movie):
        for movie_u in user.neutral_ratings:
            if movie_u == movie:
                return movie_u
        return 0

    #confirme si user à déja vu le film movie
    def user_already_see_movie(user,movie):
        if search_in_good_ratings(user,movie)==0:
            if search_in_bad_ratings==0:
                if search_in_neutral_ratings==0:
                    return 1
        return -1

    # Enregistre un utilisateur de test s'il n'existe pas déjà et le retourne
    def register_test_user(self, sender):
        if sender not in self.test_users.keys():
            self.test_users[sender] = User(sender)
        return self.test_users[sender]

    # Enregistre un utilisateur s'il n'existe pas déjà et le retourne
    def register_user(self, sender):
        if sender not in self.users.keys():
            self.users[sender] = User(sender)
        return self.users[sender]

    # Retourne les films aimés par un utilisateu print("my similarity " + str(tmp))r
    def get_movies_from_user(self, user):
        movies_list = []
        good_movies = user.good_ratings
        for movie_number in good_movies:
            movies_list.append(self.find_movie(movie_number).title)
        return movies_list

    #affiche ma liste
    def affiche_recommendation_list(self,liste):
        for i in liste:
            print("value: "+str(i[0])+" user : " + str(i[1]))

    #affiche une liste quelconque
    def print_liste(self,liste):
        for i in range(0,len(liste)):
            print("value of print "+str(liste[i]))

    #return a list that contains the first five user of the list given in arg
    def five_first_user(self, list_user):
        rep_list=[]
        cpt=0
        for usr in list_user:
            if cpt==5:
                return rep_list
            else:
                rep_list.append(usr[1])
                cpt=cpt+1
        return rep_list
    
    #retourne une liste des films aimé par les five_user sans les films déjà vu par user
    def delete_movie_already_see(self,user,list_users):
        rep_list=[]
        for usrs in list_users:
            movie_list=get_movies_from_user(usrs)
            for movies in movie_list:
                if user_already_see_movie(user,movies)==1:
                    rep_list.append(movies)
        return sorted(rep_list)

    #retourne une liste de film à recommandé
    def recommended_movie(self,user,list_movie):
        last_movie=None
        pred_movie=None
        rep_list=[]
        for movie in list_movie:
            if movie==pred_movie and movie != last_movie:
                rep_list.append(movie)
                last_movie=movie
            pred_movie=movie
        return rep_list
                
    # Affiche la recommandation pour l'utilisateur
    def make_recommendation(self, user):
        list_of_recommendation = self.compute_all_similarities(user)
        sort_list= sorted(list_of_recommendation, key=lambda tup: tup[0],reverse=True)
        five_user= self.five_first_user(sort_list)
        self.print_liste(five_user)
        #self.affiche_recommendation_list(sort_list)
        print("The best us er for recommendation "+ str(sort_list[0]))
        return sort_list[0][1]

    def find_movie(self,mov_id):
        for movie in self.movies:
            if movie.id == mov_id:
                return movie
        return None
    
    # Pose une question à l'utilisateur
    def ask_question(self, user):
        i = randint(0,len(self.movies_list))
        mov_id = self.movies_list[i]
        movie = self.find_movie(mov_id)
        if movie == None :
            tmp = self.movies[0]
        else :
            tmp = movie
        User.set_question(user,tmp.id)
        return "Avez vous aimé le film "+tmp.title
   

    
    # Calcule la similarité entre 2 utilisateurs
    @staticmethod
    def get_similarity(user_a, user_b):
        similarity = 0
        for movie in user_a.good_ratings:
            tmp_movie = Recommendation.search_in_good_ratings(user_b,movie)
            if tmp_movie != 0:
                similarity = similarity + movie*tmp_movie
            else :
                tmp_movie = Recommendation.search_in_bad_ratings(user_b,movie)
                similarity = similarity + movie*tmp_movie

        for movie in user_a.bad_ratings:
            tmp_movie = Recommendation.search_in_good_ratings(user_b,movie)
            if tmp_movie != 0:
                similarity = similarity + (-1*movie)*tmp_movie
            else :
                tmp_movie = Recommendation.search_in_bad_ratings(user_b,movie)
                similarity = similarity + (-1*movie)*tmp_movie
        return int(similarity/user_a.get_norm())
        

    # Calcule la similarité entre un utilisateur et tous les utilisateurs de tests
    def compute_all_similarities(self, user):
        list_of_similarity = []
        for id in self.test_users:
            tmp= Recommendation.get_similarity(user,self.test_users[id])
            list_of_similarity.append((tmp,id))
        return list_of_similarity
