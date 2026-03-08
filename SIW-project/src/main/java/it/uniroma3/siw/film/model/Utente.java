package it.uniroma3.siw.film.model;

import static javax.persistence.CascadeType.ALL;
import static javax.persistence.GenerationType.AUTO;

import java.util.LinkedList;
import java.util.List;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.OneToMany;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;

import lombok.Getter;
import lombok.Setter;
import lombok.Singular;

@Entity
@Getter @Setter
public class Utente {

    @Id
    @GeneratedValue(strategy = AUTO)
    private Long id;

    @NotBlank
    @Size(min = 2, max = 20)
    private String nome;

    @NotBlank
    @Size(min = 2, max = 20)
    private String cognome;

    @Singular
    @OneToMany(mappedBy = "utente", cascade = ALL)
    private List<Recensione> recensioni;

    private String urlImg;

    public Utente(){
        this.recensioni = new LinkedList<>();
    }
    
}
