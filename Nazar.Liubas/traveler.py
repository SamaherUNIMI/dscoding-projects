import pandas as pd
from city import City


class Traveler:
    def __init__(self, path):
        '''

        :param path: str
        '''
        self.cities_data = pd.read_excel(path, engine='openpyxl')
        self.cities = {}
        self.build_city_graph()

    def row_to_city(self, row):
        '''

        :param row: Series, row of DataFrame
        :return: City
        '''
        return City(row['city_ascii'], row['lat'], row['lng'],
                    row['country'], row['population'], row['id'])

    def build_city_graph(self):
        '''

        :return:
        '''
        for index, row in self.cities_data.iterrows():
            city = self.row_to_city(row)
            self.cities[row['id']] = city

        # 'id' is a unique identifier for each city
        ind = 0
        for index, row in self.cities_data.iterrows():

            print(ind)
            ind += 1

            current_city = self.cities[row['id']]
            closest_neighbors = self.find_closest_neighbors(current_city, n=4)

            n_closest = 1
            for neighbor_row in closest_neighbors.itertuples(index=False):
                neighbor = self.cities[neighbor_row.id]
                if current_city != neighbor:
                    travel_time = current_city.calc_travel_time(neighbor, n_closest=n_closest)
                    current_city.add_neighbor(neighbor, travel_time)
                    n_closest += 1

    def find_closest_neighbors(self, city, n=4):
        '''

        :param city: City
        :param n: int, number of closest city including the current one
        :return:
        '''
        # TODO optimize
        # Find the n closest neighbors based on latitude and longitude
        distances = self.cities_data.apply(lambda row: city.calculate_distance(self.row_to_city(row)), axis=1)
        closest_neighbors = self.cities_data.iloc[distances.argsort()[:n]]

        return closest_neighbors

# Code for testing
# TODO delete
x = Traveler('worldcities.xlsx')

# data = pd.read_excel('worldcities.xlsx', engine='openpyxl')
# #London
# source_city_row = data[data['id']==1826645935]
# source_city = City(source_city_row['city_ascii'].iloc[0], source_city_row['lat'].iloc[0],
#                    source_city_row['lng'].iloc[0], source_city_row['country'].iloc[0],
#                    source_city_row['population'].iloc[0], source_city_row['id'].iloc[0])
# print(source_city)

# print(x.find_closest_neighbors(source_city, 4).head())

# Tokyo - 1392685764
print(x.cities[1826645935].neighbors)
#