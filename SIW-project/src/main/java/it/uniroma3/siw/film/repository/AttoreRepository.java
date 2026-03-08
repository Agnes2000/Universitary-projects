package it.uniroma3.siw.film.repository;

import org.springframework.data.repository.CrudRepository;


import it.uniroma3.siw.film.model.Attore;


public interface AttoreRepository extends CrudRepository<Attore, Long> {
    
}