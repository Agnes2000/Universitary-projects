package it.uniroma3.siw.film.services;

import static java.util.stream.Collectors.toList;
import static java.util.stream.StreamSupport.stream;

import javax.transaction.Transactional;

import java.util.List;
import org.springframework.stereotype.Service;

import it.uniroma3.siw.film.model.Attore;
import it.uniroma3.siw.film.repository.AttoreRepository;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class AttoreService {
    
    private final AttoreRepository attoreRepository;

    @Transactional
    public Attore salvaAttore(Attore attore){
        return this.attoreRepository.save(attore);
    }

    public List<Attore> getAttori(){
        return stream(this.attoreRepository.findAll().spliterator(), false).collect(toList());
    }

    @Transactional
    public Attore getAttore(Long id){
        return this.attoreRepository.findById(id).get();
    }

    @Transactional
    public void cancellaAttore(Long id){
        this.attoreRepository.deleteById(id);
    }
}
