package it.uniroma3.siw.film.services;

import static java.lang.Math.toIntExact;
import static java.util.stream.Collectors.toList;
import static java.util.stream.StreamSupport.stream;

import java.util.List;

import javax.transaction.Transactional;

import org.springframework.stereotype.Service;

import it.uniroma3.siw.film.model.Film;
import it.uniroma3.siw.film.repository.FilmRepository;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class FilmService {
    
    private final FilmRepository filmRepository;

    @Transactional
    public Film salvaFilm(Film film) {
        return this.filmRepository.save(film);
    }

    @Transactional
    public void cancellaFilm(Long id) {
        this.filmRepository.deleteById(id);
    }

    @Transactional
    public List<Film> getFilms() {
        return stream(this.filmRepository.findAll().spliterator(), false).collect(toList());
    }

    @Transactional
    public List<Film> getTop5Film(Short anno) {
        return this.filmRepository.findAllTop5OrderByAnno();
    }
    
    @Transactional
    public Film getFilm(Long id) {
        return this.filmRepository.findById(id).get();
    }
    
    @Transactional
    public int contaFilms() {
        return toIntExact(this.filmRepository.count());
    }

    @Transactional
    public boolean esisteFilm(String nome, Short anno) {
        return this.filmRepository.existsByNomeAndAnno(nome, anno);
    }
}
