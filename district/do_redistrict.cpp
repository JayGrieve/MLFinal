#include <iostream>
#include <fstream>
#include "assignment.hpp"
#include "random.hpp"
#include "redistrict.hpp"
#include "print_out_solution.hpp"

using namespace std;

int main(int argc, char *argv[]){
  seed_rand(0);

  if(argc!=3){
    cout<<"Syntax: "<<argv[0]<<" <Number of Districts> <Population Data>"<<std::endl;
    return -1;
  }

  int num_centers = atoi(argv[1]);
  //  string client_filename = argv[2];
  std::ifstream inf(argv[2]);
  vector<Point> clients;
  vector<long> populations_vec;
  double x, y;
  int population;
  while (inf >> x >> y >> population){
    if (population > 0){
      clients.push_back(Point(x,y));
      populations_vec.push_back(population);
    }
  }

  //Shuffle centers
  for(unsigned int i=0;i<clients.size()-2;i++){
    const int j = uniform_rand_int(i,clients.size()-1);
    std::swap(clients[i], clients[j]);
    std::swap(populations_vec[i], populations_vec[j]);
  }

  std::vector<Point> centers;
  Assignment assignment;
  std::vector<double> weights;

  choose_centers(clients, &populations_vec[0], num_centers, centers, assignment, weights);


  print_out(centers, weights, clients, assignment);
}
